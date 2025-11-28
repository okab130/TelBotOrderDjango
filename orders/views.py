from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q, Sum, Count
from decimal import Decimal

from .models import (
    Store, Table, Category, MenuItem, MenuItemImage,
    Session, Order, OrderItem, StaffCall, Payment, User
)
from .serializers import (
    StoreSerializer, TableSerializer, CategorySerializer,
    MenuItemSerializer, MenuItemListSerializer, MenuItemImageSerializer,
    SessionSerializer, SessionCreateSerializer,
    OrderSerializer, OrderCreateSerializer,
    OrderItemSerializer,
    StaffCallSerializer, StaffCallCreateSerializer,
    PaymentSerializer, PaymentRequestSerializer,
    UserSerializer
)


class StoreViewSet(viewsets.ModelViewSet):
    """店舗API"""
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]


class TableViewSet(viewsets.ModelViewSet):
    """テーブルAPI"""
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def by_qr_code(self, request):
        """QRコードでテーブル情報を取得"""
        qr_code_url = request.query_params.get('qr_code_url')
        if not qr_code_url:
            return Response(
                {'error': 'qr_code_urlパラメータが必要です'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            table = Table.objects.get(qr_code_url=qr_code_url, is_available=True)
            serializer = self.get_serializer(table)
            return Response(serializer.data)
        except Table.DoesNotExist:
            return Response(
                {'error': 'テーブルが見つかりません'},
                status=status.HTTP_404_NOT_FOUND
            )


class CategoryViewSet(viewsets.ModelViewSet):
    """カテゴリAPI"""
    queryset = Category.objects.filter(is_active=True).order_by('display_order')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        store_id = self.request.query_params.get('store_id')
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        return queryset


class MenuItemViewSet(viewsets.ModelViewSet):
    """メニュー項目API"""
    queryset = MenuItem.objects.filter(is_active=True).order_by('display_order')
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        store_id = self.request.query_params.get('store_id')
        category_id = self.request.query_params.get('category_id')
        available_only = self.request.query_params.get('available_only')
        
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if available_only == 'true':
            queryset = queryset.filter(is_available=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MenuItemListSerializer
        return MenuItemSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_available(self, request, pk=None):
        """売り切れ状態を切り替え"""
        menu_item = self.get_object()
        menu_item.is_available = not menu_item.is_available
        menu_item.save()
        serializer = self.get_serializer(menu_item)
        return Response(serializer.data)


class SessionViewSet(viewsets.ModelViewSet):
    """セッションAPI"""
    queryset = Session.objects.all().order_by('-started_at')
    serializer_class = SessionSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        session_code = self.request.query_params.get('session_code')
        table_id = self.request.query_params.get('table_id')
        active_only = self.request.query_params.get('active_only')
        
        if session_code:
            queryset = queryset.filter(session_code=session_code)
        if table_id:
            queryset = queryset.filter(table_id=table_id)
        if active_only == 'true':
            queryset = queryset.filter(status__in=['active', 'calling_staff', 'payment_requested'])
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = SessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 既存セッションがあればそれを返す
        if 'existing_session' in serializer.validated_data:
            existing_session = serializer.validated_data['existing_session']
            response_serializer = SessionSerializer(existing_session)
            return Response(
                {
                    'session': response_serializer.data,
                    'is_new': False,
                    'message': '既存のセッションに接続しました'
                },
                status=status.HTTP_200_OK
            )
        
        # 新規セッション作成
        session = serializer.save()
        response_serializer = SessionSerializer(session)
        return Response(
            {
                'session': response_serializer.data,
                'is_new': True,
                'message': '新しいセッションを作成しました'
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def complete(self, request, pk=None):
        """セッションを完了"""
        session = self.get_object()
        session.status = 'completed'
        session.ended_at = timezone.now()
        session.save()
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def orders(self, request, pk=None):
        """セッションの全注文を取得"""
        session = self.get_object()
        orders = session.order_set.all().order_by('order_number')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    """注文API"""
    queryset = Order.objects.all().order_by('-ordered_at')
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        session_id = self.request.query_params.get('session_id')
        status_filter = self.request.query_params.get('status')
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """注文ステータスを更新"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES).keys():
            return Response(
                {'error': '無効なステータスです'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        
        # ステータスに応じて日時を記録
        if new_status == 'cooking' and not order.cooking_started_at:
            order.cooking_started_at = timezone.now()
        elif new_status == 'ready' and not order.ready_at:
            order.ready_at = timezone.now()
        elif new_status == 'served' and not order.served_at:
            order.served_at = timezone.now()
        elif new_status == 'cancelled':
            order.cancelled_at = timezone.now()
            if request.user.is_authenticated:
                order.cancelled_by = request.user
        
        order.save()
        
        # 注文明細のステータスも更新
        order.items.update(status=new_status)
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def dashboard(self, request):
        """調理ダッシュボード用データ"""
        # 未完了の注文を取得
        orders = Order.objects.filter(
            status__in=['pending', 'cooking', 'ready']
        ).select_related('session', 'session__table').prefetch_related('items').order_by('ordered_at')
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderItemViewSet(viewsets.ModelViewSet):
    """注文明細API"""
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """注文明細のステータスを更新"""
        order_item = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(OrderItem.STATUS_CHOICES).keys():
            return Response(
                {'error': '無効なステータスです'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order_item.status = new_status
        order_item.save()
        
        # 全ての明細が同じステータスになったら注文のステータスも更新
        order = order_item.order
        all_items_same_status = all(
            item.status == new_status 
            for item in order.items.all()
        )
        
        if all_items_same_status and order.status != new_status:
            order.status = new_status
            
            if new_status == 'cooking' and not order.cooking_started_at:
                order.cooking_started_at = timezone.now()
            elif new_status == 'ready' and not order.ready_at:
                order.ready_at = timezone.now()
            elif new_status == 'served' and not order.served_at:
                order.served_at = timezone.now()
            
            order.save()
        
        serializer = self.get_serializer(order_item)
        return Response(serializer.data)


class StaffCallViewSet(viewsets.ModelViewSet):
    """店員呼び出しAPI"""
    queryset = StaffCall.objects.all().order_by('-called_at')
    serializer_class = StaffCallSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        session_id = self.request.query_params.get('session_id')
        pending_only = self.request.query_params.get('pending_only')
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        if pending_only == 'true':
            queryset = queryset.filter(status='pending')
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = StaffCallCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff_call = serializer.save()
        response_serializer = StaffCallSerializer(staff_call)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def respond(self, request, pk=None):
        """呼び出しに対応開始"""
        staff_call = self.get_object()
        staff_call.status = 'in_progress'
        staff_call.responded_at = timezone.now()
        staff_call.save()
        
        # セッションのステータスを戻す
        if staff_call.session.status == 'calling_staff':
            staff_call.session.status = 'active'
            staff_call.session.save()
        
        serializer = self.get_serializer(staff_call)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def resolve(self, request, pk=None):
        """呼び出しを解決"""
        staff_call = self.get_object()
        staff_call.status = 'resolved'
        staff_call.resolved_at = timezone.now()
        staff_call.save()
        serializer = self.get_serializer(staff_call)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    """会計API"""
    queryset = Payment.objects.all().order_by('-requested_at')
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        pending_only = self.request.query_params.get('pending_only')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if pending_only == 'true':
            queryset = queryset.filter(status='pending')
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = PaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        response_serializer = PaymentSerializer(payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """会計を完了"""
        payment = self.get_object()
        payment_method = request.data.get('payment_method')
        
        if payment_method not in dict(Payment.PAYMENT_METHOD_CHOICES).keys():
            return Response(
                {'error': '無効な支払い方法です'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.payment_method = payment_method
        payment.status = 'paid'
        payment.paid_at = timezone.now()
        payment.save()
        
        # セッションを完了
        payment.session.status = 'completed'
        payment.session.ended_at = timezone.now()
        payment.session.save()
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)


# Telegram Bot関連ビュー
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import asyncio
from .telegram_bot import telegram_bot


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(APIView):
    """Telegram Bot Webhook受信エンドポイント"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Webhookからのアップデートを受信"""
        try:
            update_data = request.data
            
            # 非同期処理を実行
            asyncio.run(telegram_bot.process_update(update_data))
            
            return Response({'status': 'ok'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


from django.shortcuts import render


def miniapp_view(request):
    """Telegram Mini Apps画面"""
    return render(request, 'miniapp.html')
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def cancel(self, request, pk=None):
        """会計をキャンセル"""
        payment = self.get_object()
        payment.status = 'cancelled'
        payment.save()
        
        # セッションステータスを戻す
        payment.session.status = 'active'
        payment.session.save()
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """ユーザーAPI"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
