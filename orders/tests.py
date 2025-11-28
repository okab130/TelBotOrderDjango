from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from .models import (
    Store, Table, Category, MenuItem,
    Session, Order, OrderItem, User
)


class MenuItemAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # テストデータ作成
        self.store = Store.objects.create(
            name='テスト店舗',
            is_active=True
        )
        
        self.category = Category.objects.create(
            store=self.store,
            name='前菜',
            display_order=1
        )
        
        self.menu_item = MenuItem.objects.create(
            store=self.store,
            category=self.category,
            name='テスト商品',
            description='テスト説明',
            price=Decimal('1000.00'),
            is_available=True
        )
    
    def test_list_menu_items(self):
        """メニュー一覧取得テスト"""
        response = self.client.get('/api/menu-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'テスト商品')
    
    def test_filter_by_category(self):
        """カテゴリフィルタリングテスト"""
        response = self.client.get(f'/api/menu-items/?category_id={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class SessionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.store = Store.objects.create(name='テスト店舗')
        self.table = Table.objects.create(
            store=self.store,
            table_number='A-1',
            qr_code_url='https://test.com/table-a1'
        )
    
    def test_create_session(self):
        """セッション作成テスト"""
        data = {
            'qr_code_url': self.table.qr_code_url,
            'party_size': 4
        }
        response = self.client.post('/api/sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_new'])
        self.assertEqual(response.data['session']['party_size'], 4)
    
    def test_resume_existing_session(self):
        """既存セッション復帰テスト"""
        # 最初のセッション作成
        session = Session.objects.create(
            store=self.store,
            table=self.table,
            session_code='TEST123',
            party_size=4,
            status='active',
            started_at=timezone.now()
        )
        
        # 同じテーブルで新規セッション作成を試みる
        data = {
            'qr_code_url': self.table.qr_code_url,
            'party_size': 2
        }
        response = self.client.post('/api/sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_new'])
        self.assertEqual(response.data['session']['session_code'], 'TEST123')


class OrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.store = Store.objects.create(name='テスト店舗')
        self.table = Table.objects.create(
            store=self.store,
            table_number='A-1',
            qr_code_url='https://test.com/table-a1'
        )
        self.session = Session.objects.create(
            store=self.store,
            table=self.table,
            session_code='TEST123',
            party_size=4,
            status='active',
            started_at=timezone.now()
        )
        
        self.category = Category.objects.create(
            store=self.store,
            name='前菜',
            display_order=1
        )
        
        self.menu_item1 = MenuItem.objects.create(
            store=self.store,
            category=self.category,
            name='商品1',
            price=Decimal('1000.00'),
            is_available=True
        )
        
        self.menu_item2 = MenuItem.objects.create(
            store=self.store,
            category=self.category,
            name='商品2',
            price=Decimal('500.00'),
            is_available=True
        )
    
    def test_create_order(self):
        """注文作成テスト"""
        data = {
            'session_code': self.session.session_code,
            'telegram_user_id': 'user123',
            'telegram_username': 'テストユーザー',
            'items': [
                {
                    'menu_item_id': self.menu_item1.id,
                    'quantity': 2,
                    'note': 'テスト備考'
                },
                {
                    'menu_item_id': self.menu_item2.id,
                    'quantity': 1
                }
            ]
        }
        
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order_number'], 1)
        self.assertEqual(response.data['total_amount'], '2500.00')
        self.assertEqual(len(response.data['items']), 2)
    
    def test_order_unavailable_item(self):
        """売り切れ商品の注文エラーテスト"""
        self.menu_item1.is_available = False
        self.menu_item1.save()
        
        data = {
            'session_code': self.session.session_code,
            'items': [
                {
                    'menu_item_id': self.menu_item1.id,
                    'quantity': 1
                }
            ]
        }
        
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_order_status_update(self):
        """注文ステータス更新テスト"""
        # まず注文を作成
        order = Order.objects.create(
            session=self.session,
            order_number=1,
            total_amount=Decimal('1000.00'),
            status='pending',
            ordered_at=timezone.now()
        )
        
        # 管理者ユーザーでログイン
        user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            store=self.store,
            role='admin'
        )
        self.client.force_authenticate(user=user)
        
        # ステータスを調理中に更新
        response = self.client.post(
            f'/api/orders/{order.id}/update_status/',
            {'status': 'cooking'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cooking')
        
        # DBから再取得して確認
        order.refresh_from_db()
        self.assertEqual(order.status, 'cooking')
        self.assertIsNotNone(order.cooking_started_at)


class StaffCallAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.store = Store.objects.create(name='テスト店舗')
        self.table = Table.objects.create(
            store=self.store,
            table_number='A-1',
            qr_code_url='https://test.com/table-a1'
        )
        self.session = Session.objects.create(
            store=self.store,
            table=self.table,
            session_code='TEST123',
            party_size=4,
            status='active',
            started_at=timezone.now()
        )
    
    def test_create_staff_call(self):
        """店員呼び出し作成テスト"""
        data = {
            'session_code': self.session.session_code,
            'reason': 'water',
            'message': 'お水を2つください'
        }
        
        response = self.client.post('/api/staff-calls/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reason'], 'water')
        self.assertEqual(response.data['status'], 'pending')
        
        # セッションステータスが更新されているか確認
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, 'calling_staff')


class PaymentAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.store = Store.objects.create(name='テスト店舗')
        self.table = Table.objects.create(
            store=self.store,
            table_number='A-1',
            qr_code_url='https://test.com/table-a1'
        )
        self.session = Session.objects.create(
            store=self.store,
            table=self.table,
            session_code='TEST123',
            party_size=4,
            status='active',
            started_at=timezone.now()
        )
        
        # テスト用注文を作成
        self.order = Order.objects.create(
            session=self.session,
            order_number=1,
            total_amount=Decimal('3000.00'),
            status='served',
            ordered_at=timezone.now()
        )
    
    def test_create_payment_request(self):
        """会計依頼作成テスト"""
        data = {
            'session_code': self.session.session_code
        }
        
        response = self.client.post('/api/payments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_amount'], '3000.00')
        self.assertEqual(response.data['status'], 'pending')
        
        # セッションステータスが更新されているか確認
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, 'payment_requested')
    
    def test_payment_without_orders(self):
        """注文がない場合の会計依頼エラーテスト"""
        # 注文を削除
        self.order.delete()
        
        data = {
            'session_code': self.session.session_code
        }
        
        response = self.client.post('/api/payments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_complete_payment(self):
        """会計完了テスト"""
        # まず会計依頼を作成
        from .models import Payment
        payment = Payment.objects.create(
            session=self.session,
            total_amount=Decimal('3000.00'),
            status='pending',
            requested_at=timezone.now()
        )
        
        # 管理者ユーザーでログイン
        user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            store=self.store,
            role='admin'
        )
        self.client.force_authenticate(user=user)
        
        # 会計完了
        response = self.client.post(
            f'/api/payments/{payment.id}/complete/',
            {'payment_method': 'cash'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'paid')
        self.assertEqual(response.data['payment_method'], 'cash')
        
        # セッションが完了になっているか確認
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, 'completed')

