from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from orders.models import (
    Store, Table, Category, MenuItem,
    Session, Order, OrderItem, User
)


class Command(BaseCommand):
    help = 'テストデータを作成'

    def handle(self, *args, **options):
        self.stdout.write('テストデータを作成しています...')
        
        # 既存データをクリア
        self.stdout.write('既存データをクリア中...')
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Session.objects.all().delete()
        MenuItem.objects.all().delete()
        Category.objects.all().delete()
        Table.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Store.objects.all().delete()
        
        # 店舗を作成
        self.stdout.write('店舗を作成中...')
        store = Store.objects.create(
            name='テスト居酒屋',
            address='東京都渋谷区1-2-3',
            phone='03-1234-5678',
            business_hours='{"weekday": "17:00-23:00", "weekend": "16:00-24:00"}',
            is_active=True
        )
        
        # テーブルを作成
        self.stdout.write('テーブルを作成中...')
        tables = []
        for table_num in ['A-1', 'A-2', 'A-3', 'B-1', 'B-2', 'B-3', 'C-1', 'C-2']:
            table = Table.objects.create(
                store=store,
                table_number=table_num,
                qr_code_url=f'https://t.me/yourbot?start=table-{table_num}',
                capacity=4,
                is_available=True
            )
            tables.append(table)
        
        # カテゴリを作成
        self.stdout.write('カテゴリを作成中...')
        categories = {
            '前菜': Category.objects.create(store=store, name='前菜', display_order=1),
            'メイン': Category.objects.create(store=store, name='メイン', display_order=2),
            '飲み物': Category.objects.create(store=store, name='飲み物', display_order=3),
            'デザート': Category.objects.create(store=store, name='デザート', display_order=4),
        }
        
        # メニュー項目を作成
        self.stdout.write('メニュー項目を作成中...')
        menu_items = []
        
        # 前菜
        menu_items.append(MenuItem.objects.create(
            store=store,
            category=categories['前菜'],
            name='シーザーサラダ',
            description='新鮮なロメインレタスとクリーミーなシーザードレッシング、パルメザンチーズをトッピング',
            price=Decimal('850.00'),
            display_order=1,
            is_available=True
        ))
        
        menu_items.append(MenuItem.objects.create(
            store=store,
            category=categories['前菜'],
            name='枝豆',
            description='塩茹で枝豆',
            price=Decimal('400.00'),
            display_order=2,
            is_available=True
        ))
        
        menu_items.append(MenuItem.objects.create(
            store=store,
            category=categories['前菜'],
            name='唐揚げ',
            description='ジューシーな鶏の唐揚げ',
            price=Decimal('800.00'),
            display_order=3,
            is_available=True
        ))
        
        # メイン
        menu_items.append(MenuItem.objects.create(
            store=store,
            category=categories['メイン'],
            name='トマトパスタ',
            description='完熟トマトのフレッシュソース',
            price=Decimal('1200.00'),
            display_order=1,
            is_available=False  # 売り切れ
        ))
        
        menu_items.append(MenuItem.objects.create(
            store=store,
            category=categories['メイン'],
            name='ハンバーグステーキ',
            description='ジューシーなハンバーグステーキ',
            price=Decimal('1500.00'),
            display_order=2,
            is_available=True
        ))
        
        menu_items.append(MenuItem.objects.create(
            store=store,
            category=categories['メイン'],
            name='カルボナーラ',
            description='濃厚なカルボナーラソース',
            price=Decimal('1300.00'),
            display_order=3,
            is_available=True
        ))
        
        # 飲み物
        menu_items.append(MenuItem.objects.create(
            store=store,
            category=categories['飲み物'],
            name='ビール',
            description='キンキンに冷えた生ビール',
            price=Decimal('600.00'),
            display_order=1,
            is_available=True
        ))
        
        menu_items.append(MenuItem.objects.create(
            store=store,
            category=categories['飲み物'],
            name='ハイボール',
            description='爽やかなハイボール',
            price=Decimal('500.00'),
            display_order=2,
            is_available=True
        ))
        
        menu_items.append(MenuItem.objects.create(
            store=store,
            category=categories['飲み物'],
            name='ウーロン茶',
            description='さっぱりウーロン茶',
            price=Decimal('300.00'),
            display_order=3,
            is_available=True
        ))
        
        # デザート
        menu_items.append(MenuItem.objects.create(
            store=store,
            category=categories['デザート'],
            name='チーズケーキ',
            description='濃厚なベイクドチーズケーキ',
            price=Decimal('600.00'),
            display_order=1,
            is_available=True
        ))
        
        menu_items.append(MenuItem.objects.create(
            store=store,
            category=categories['デザート'],
            name='アイスクリーム',
            description='バニラアイスクリーム',
            price=Decimal('400.00'),
            display_order=2,
            is_available=True
        ))
        
        # スタッフユーザーを作成
        self.stdout.write('スタッフユーザーを作成中...')
        
        # 管理者
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                store=store,
                role='admin'
            )
        
        # 料理人
        User.objects.create_user(
            username='chef1',
            email='chef1@example.com',
            password='chef123',
            store=store,
            role='chef'
        )
        
        # スーパーバイザ
        User.objects.create_user(
            username='supervisor1',
            email='supervisor1@example.com',
            password='super123',
            store=store,
            role='supervisor'
        )
        
        # セッションとサンプル注文を作成
        self.stdout.write('サンプルセッションと注文を作成中...')
        
        # アクティブなセッション1
        session1 = Session.objects.create(
            store=store,
            table=tables[0],  # A-1
            session_code=f'TBL1-{timezone.now().strftime("%Y%m%d")}-ABC123',
            party_size=4,
            status='active',
            started_at=timezone.now() - timezone.timedelta(minutes=30)
        )
        
        # 注文1-1
        order1_1 = Order.objects.create(
            session=session1,
            telegram_user_id='user001',
            telegram_username='田中太郎',
            order_number=1,
            total_amount=Decimal('2900.00'),
            status='served',
            ordered_at=timezone.now() - timezone.timedelta(minutes=25),
            cooking_started_at=timezone.now() - timezone.timedelta(minutes=23),
            ready_at=timezone.now() - timezone.timedelta(minutes=15),
            served_at=timezone.now() - timezone.timedelta(minutes=10)
        )
        
        OrderItem.objects.create(
            order=order1_1,
            menu_item=menu_items[0],  # シーザーサラダ
            menu_item_name=menu_items[0].name,
            unit_price=menu_items[0].price,
            quantity=2,
            subtotal=menu_items[0].price * 2,
            status='served'
        )
        
        OrderItem.objects.create(
            order=order1_1,
            menu_item=menu_items[6],  # ビール
            menu_item_name=menu_items[6].name,
            unit_price=menu_items[6].price,
            quantity=2,
            subtotal=menu_items[6].price * 2,
            status='served'
        )
        
        # 注文1-2
        order1_2 = Order.objects.create(
            session=session1,
            telegram_user_id='user002',
            telegram_username='山田花子',
            order_number=2,
            total_amount=Decimal('1200.00'),
            status='cooking',
            ordered_at=timezone.now() - timezone.timedelta(minutes=10),
            cooking_started_at=timezone.now() - timezone.timedelta(minutes=8)
        )
        
        OrderItem.objects.create(
            order=order1_2,
            menu_item=menu_items[1],  # 枝豆
            menu_item_name=menu_items[1].name,
            unit_price=menu_items[1].price,
            quantity=1,
            subtotal=menu_items[1].price,
            status='cooking'
        )
        
        OrderItem.objects.create(
            order=order1_2,
            menu_item=menu_items[2],  # 唐揚げ
            menu_item_name=menu_items[2].name,
            unit_price=menu_items[2].price,
            quantity=1,
            subtotal=menu_items[2].price,
            status='cooking'
        )
        
        # アクティブなセッション2
        session2 = Session.objects.create(
            store=store,
            table=tables[3],  # B-1
            session_code=f'TBL4-{timezone.now().strftime("%Y%m%d")}-DEF456',
            party_size=2,
            status='active',
            started_at=timezone.now() - timezone.timedelta(minutes=15)
        )
        
        # 注文2-1
        order2_1 = Order.objects.create(
            session=session2,
            telegram_user_id='user003',
            telegram_username='佐藤次郎',
            order_number=1,
            total_amount=Decimal('1500.00'),
            status='pending',
            ordered_at=timezone.now() - timezone.timedelta(minutes=5)
        )
        
        OrderItem.objects.create(
            order=order2_1,
            menu_item=menu_items[4],  # ハンバーグステーキ
            menu_item_name=menu_items[4].name,
            unit_price=menu_items[4].price,
            quantity=1,
            subtotal=menu_items[4].price,
            status='pending'
        )
        
        self.stdout.write(self.style.SUCCESS('テストデータの作成が完了しました！'))
        self.stdout.write('')
        self.stdout.write(f'店舗: {store.name}')
        self.stdout.write(f'テーブル: {len(tables)}個')
        self.stdout.write(f'カテゴリ: {len(categories)}個')
        self.stdout.write(f'メニュー項目: {len(menu_items)}個')
        self.stdout.write(f'セッション: 2個')
        self.stdout.write(f'注文: 3個')
        self.stdout.write('')
        self.stdout.write('ログイン情報:')
        self.stdout.write('  管理者 - username: admin, password: admin123')
        self.stdout.write('  料理人 - username: chef1, password: chef123')
        self.stdout.write('  スーパーバイザ - username: supervisor1, password: super123')
