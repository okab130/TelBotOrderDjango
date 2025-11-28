from rest_framework import serializers
from .models import (
    Store, Table, Category, MenuItem, MenuItemImage,
    Session, Order, OrderItem, StaffCall, Payment, User
)
from decimal import Decimal
from django.utils import timezone


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MenuItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemImage
        fields = '__all__'


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = MenuItemImageSerializer(many=True, read_only=True, source='menuitemimage_set')
    
    class Meta:
        model = MenuItem
        fields = '__all__'


class MenuItemListSerializer(serializers.ModelSerializer):
    """メニュー一覧用の軽量シリアライザ"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'price', 
            'category_id', 'category_name', 'thumbnail_url',
            'is_available', 'is_active', 'max_quantity_per_order'
        ]
    
    def get_thumbnail_url(self, obj):
        if obj.image_thumbnail_path:
            return obj.image_thumbnail_path
        return None


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class OrderItemCreateSerializer(serializers.Serializer):
    """注文明細作成用"""
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=99)
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    table_number = serializers.CharField(source='session.table.table_number', read_only=True)
    telegram_username = serializers.CharField(read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'ordered_at']


class OrderCreateSerializer(serializers.Serializer):
    """注文作成用"""
    session_code = serializers.CharField(max_length=50)
    telegram_user_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    telegram_username = serializers.CharField(max_length=100, required=False, allow_blank=True)
    items = OrderItemCreateSerializer(many=True)
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("注文には少なくとも1つの商品が必要です")
        return value
    
    def validate(self, data):
        # セッションの存在確認
        try:
            session = Session.objects.get(session_code=data['session_code'])
            if session.status not in ['active', 'payment_requested']:
                raise serializers.ValidationError("このセッションは注文できません")
            data['session'] = session
        except Session.DoesNotExist:
            raise serializers.ValidationError("セッションが見つかりません")
        
        # メニュー項目の検証
        total_amount = Decimal('0.00')
        validated_items = []
        
        for item_data in data['items']:
            try:
                menu_item = MenuItem.objects.get(
                    id=item_data['menu_item_id'],
                    is_active=True
                )
                
                if not menu_item.is_available:
                    raise serializers.ValidationError(
                        f"{menu_item.name} は現在提供できません"
                    )
                
                max_qty = menu_item.max_quantity_per_order or 10
                if item_data['quantity'] > max_qty:
                    raise serializers.ValidationError(
                        f"{menu_item.name} は1注文あたり{max_qty}個までです"
                    )
                
                subtotal = menu_item.price * item_data['quantity']
                total_amount += subtotal
                
                validated_items.append({
                    'menu_item': menu_item,
                    'quantity': item_data['quantity'],
                    'note': item_data.get('note', ''),
                    'subtotal': subtotal
                })
                
            except MenuItem.DoesNotExist:
                raise serializers.ValidationError(
                    f"メニュー項目(ID:{item_data['menu_item_id']})が見つかりません"
                )
        
        data['validated_items'] = validated_items
        data['total_amount'] = total_amount
        
        return data
    
    def create(self, validated_data):
        session = validated_data['session']
        
        # 注文番号を生成（セッション内での連番）
        last_order = Order.objects.filter(session=session).order_by('-order_number').first()
        order_number = (last_order.order_number + 1) if last_order else 1
        
        # 注文を作成
        order = Order.objects.create(
            session=session,
            telegram_user_id=validated_data.get('telegram_user_id', ''),
            telegram_username=validated_data.get('telegram_username', ''),
            order_number=order_number,
            total_amount=validated_data['total_amount'],
            status='pending',
            ordered_at=timezone.now()
        )
        
        # 注文明細を作成
        for item_data in validated_data['validated_items']:
            OrderItem.objects.create(
                order=order,
                menu_item=item_data['menu_item'],
                menu_item_name=item_data['menu_item'].name,
                unit_price=item_data['menu_item'].price,
                quantity=item_data['quantity'],
                subtotal=item_data['subtotal'],
                note=item_data['note'],
                status='pending'
            )
        
        return order


class SessionSerializer(serializers.ModelSerializer):
    table_number = serializers.CharField(source='table.table_number', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    orders = OrderSerializer(many=True, read_only=True, source='order_set')
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Session
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'started_at', 'session_code']
    
    def get_total_amount(self, obj):
        return sum(order.total_amount for order in obj.order_set.exclude(status='cancelled'))


class SessionCreateSerializer(serializers.Serializer):
    """セッション作成用"""
    qr_code_url = serializers.CharField(max_length=255)
    party_size = serializers.IntegerField(min_value=1, max_value=99)
    telegram_chat_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    def validate(self, data):
        # テーブルの存在確認
        try:
            table = Table.objects.get(qr_code_url=data['qr_code_url'], is_available=True)
            data['table'] = table
        except Table.DoesNotExist:
            raise serializers.ValidationError("有効なテーブルが見つかりません")
        
        # アクティブなセッションが既に存在するか確認
        existing_session = Session.objects.filter(
            table=table,
            status__in=['active', 'calling_staff', 'payment_requested']
        ).first()
        
        if existing_session:
            data['existing_session'] = existing_session
        
        return data
    
    def create(self, validated_data):
        import uuid
        
        table = validated_data['table']
        
        # セッションコードを生成
        session_code = f"TBL{table.id}-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        session = Session.objects.create(
            store=table.store,
            table=table,
            session_code=session_code,
            party_size=validated_data['party_size'],
            telegram_chat_id=validated_data.get('telegram_chat_id', ''),
            status='active',
            started_at=timezone.now()
        )
        
        return session


class StaffCallSerializer(serializers.ModelSerializer):
    table_number = serializers.CharField(source='session.table.table_number', read_only=True)
    
    class Meta:
        model = StaffCall
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'called_at']


class StaffCallCreateSerializer(serializers.Serializer):
    """店員呼び出し作成用"""
    session_code = serializers.CharField(max_length=50)
    reason = serializers.ChoiceField(choices=StaffCall.REASON_CHOICES)
    message = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate(self, data):
        try:
            session = Session.objects.get(session_code=data['session_code'])
            if session.status not in ['active', 'payment_requested']:
                raise serializers.ValidationError("このセッションからは呼び出しできません")
            data['session'] = session
        except Session.DoesNotExist:
            raise serializers.ValidationError("セッションが見つかりません")
        
        return data
    
    def create(self, validated_data):
        staff_call = StaffCall.objects.create(
            session=validated_data['session'],
            reason=validated_data['reason'],
            message=validated_data.get('message', ''),
            status='pending',
            called_at=timezone.now()
        )
        
        # セッションステータスを更新
        validated_data['session'].status = 'calling_staff'
        validated_data['session'].save()
        
        return staff_call


class PaymentSerializer(serializers.ModelSerializer):
    table_number = serializers.CharField(source='session.table.table_number', read_only=True)
    session_code = serializers.CharField(source='session.session_code', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'requested_at']


class PaymentRequestSerializer(serializers.Serializer):
    """会計依頼用"""
    session_code = serializers.CharField(max_length=50)
    
    def validate(self, data):
        try:
            session = Session.objects.get(session_code=data['session_code'])
            if session.status not in ['active', 'calling_staff']:
                raise serializers.ValidationError("このセッションは会計依頼できません")
            data['session'] = session
        except Session.DoesNotExist:
            raise serializers.ValidationError("セッションが見つかりません")
        
        # 既に会計依頼済みでないか確認
        if hasattr(session, 'payment') and session.payment.status == 'pending':
            raise serializers.ValidationError("既に会計依頼済みです")
        
        # 注文がない場合はエラー
        if not session.order_set.exists():
            raise serializers.ValidationError("注文がありません")
        
        return data
    
    def create(self, validated_data):
        session = validated_data['session']
        
        # 合計金額を計算
        total_amount = sum(
            order.total_amount 
            for order in session.order_set.exclude(status='cancelled')
        )
        
        # 既存の会計レコードがあればキャンセル
        if hasattr(session, 'payment'):
            session.payment.status = 'cancelled'
            session.payment.save()
        
        # 新しい会計レコードを作成
        payment = Payment.objects.create(
            session=session,
            total_amount=total_amount,
            status='pending',
            requested_at=timezone.now()
        )
        
        # セッションステータスを更新
        session.status = 'payment_requested'
        session.save()
        
        return payment


class UserSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'store', 'store_name', 'is_active']
        read_only_fields = ['id']
