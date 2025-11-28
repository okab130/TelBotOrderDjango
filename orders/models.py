from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal


class Store(models.Model):
    """店舗"""
    name = models.CharField('店舗名', max_length=100)
    address = models.CharField('住所', max_length=255, blank=True, null=True)
    phone = models.CharField('電話番号', max_length=20, blank=True, null=True)
    business_hours = models.TextField('営業時間', blank=True, null=True, help_text='JSON形式')
    is_active = models.BooleanField('営業中フラグ', default=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        db_table = 'store'
        verbose_name = '店舗'
        verbose_name_plural = '店舗'

    def __str__(self):
        return self.name


class Table(models.Model):
    """テーブル"""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店舗')
    table_number = models.CharField('テーブル番号', max_length=20)
    qr_code_url = models.CharField('QRコードURL', max_length=255, unique=True)
    capacity = models.IntegerField('定員数', blank=True, null=True)
    is_available = models.BooleanField('利用可能フラグ', default=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        db_table = 'table'
        verbose_name = 'テーブル'
        verbose_name_plural = 'テーブル'
        unique_together = [['store', 'table_number']]
        indexes = [
            models.Index(fields=['store', 'table_number']),
        ]

    def __str__(self):
        return f"{self.store.name} - {self.table_number}"


class Category(models.Model):
    """カテゴリ"""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店舗')
    name = models.CharField('カテゴリ名', max_length=50)
    display_order = models.IntegerField('表示順序', default=0)
    is_active = models.BooleanField('有効フラグ', default=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        db_table = 'category'
        verbose_name = 'カテゴリ'
        verbose_name_plural = 'カテゴリ'
        indexes = [
            models.Index(fields=['store', 'display_order']),
        ]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """メニュー項目"""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店舗')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='カテゴリ')
    name = models.CharField('商品名', max_length=100)
    description = models.TextField('説明', blank=True, null=True)
    price = models.DecimalField('価格', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    image_path = models.CharField('商品画像ファイルパス', max_length=500, blank=True, null=True)
    image_thumbnail_path = models.CharField('サムネイル画像パス', max_length=500, blank=True, null=True)
    max_quantity_per_order = models.IntegerField('1注文あたりの最大数量', default=10, blank=True, null=True)
    display_order = models.IntegerField('表示順序', default=0)
    is_available = models.BooleanField('提供可能フラグ', default=True, help_text='売り切れ管理')
    is_active = models.BooleanField('有効フラグ', default=True, help_text='メニュー削除')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        db_table = 'menu_item'
        verbose_name = 'メニュー項目'
        verbose_name_plural = 'メニュー項目'
        indexes = [
            models.Index(fields=['store', 'category', 'display_order']),
            models.Index(fields=['is_available', 'is_active']),
        ]

    def __str__(self):
        return self.name


class MenuItemImage(models.Model):
    """メニュー画像"""
    IMAGE_TYPE_CHOICES = [
        ('original', 'オリジナル'),
        ('thumbnail', 'サムネイル'),
        ('large', '大サイズ'),
    ]

    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name='メニュー項目')
    image_type = models.CharField('画像タイプ', max_length=20, choices=IMAGE_TYPE_CHOICES)
    file_path = models.CharField('ファイルパス', max_length=500)
    file_size = models.IntegerField('ファイルサイズ', help_text='バイト')
    width = models.IntegerField('画像幅', blank=True, null=True, help_text='ピクセル')
    height = models.IntegerField('画像高さ', blank=True, null=True, help_text='ピクセル')
    mime_type = models.CharField('MIMEタイプ', max_length=50)
    uploaded_at = models.DateTimeField('アップロード日時')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        db_table = 'menu_item_image'
        verbose_name = 'メニュー画像'
        verbose_name_plural = 'メニュー画像'
        unique_together = [['menu_item', 'image_type']]
        indexes = [
            models.Index(fields=['menu_item', 'image_type']),
        ]

    def __str__(self):
        return f"{self.menu_item.name} - {self.get_image_type_display()}"


class Session(models.Model):
    """来店セッション"""
    STATUS_CHOICES = [
        ('active', '来店中'),
        ('calling_staff', '店員呼び出し中'),
        ('payment_requested', '会計依頼中'),
        ('completed', '完了'),
        ('cancelled', 'キャンセル'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店舗')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name='テーブル')
    session_code = models.CharField('セッションコード', max_length=50, unique=True)
    party_size = models.IntegerField('来店人数')
    telegram_chat_id = models.CharField('Telegram Chat ID', max_length=50, blank=True, null=True)
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField('来店日時')
    ended_at = models.DateTimeField('退店日時', blank=True, null=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        db_table = 'session'
        verbose_name = 'セッション'
        verbose_name_plural = 'セッション'
        indexes = [
            models.Index(fields=['table', 'status']),
            models.Index(fields=['started_at']),
        ]

    def __str__(self):
        return f"{self.table} - {self.session_code}"


class Order(models.Model):
    """注文"""
    STATUS_CHOICES = [
        ('pending', '注文受付済み'),
        ('cooking', '調理中'),
        ('ready', '調理完了'),
        ('served', '提供済み'),
        ('cancelled', 'キャンセル'),
    ]

    session = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name='セッション')
    telegram_user_id = models.CharField('Telegram User ID', max_length=50, blank=True, null=True)
    telegram_username = models.CharField('Telegram Username', max_length=100, blank=True, null=True)
    order_number = models.IntegerField('注文番号')
    total_amount = models.DecimalField('合計金額', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='pending')
    ordered_at = models.DateTimeField('注文日時')
    cooking_started_at = models.DateTimeField('調理開始日時', blank=True, null=True)
    ready_at = models.DateTimeField('調理完了日時', blank=True, null=True)
    served_at = models.DateTimeField('提供日時', blank=True, null=True)
    cancelled_at = models.DateTimeField('キャンセル日時', blank=True, null=True)
    cancelled_by = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='キャンセル実行者')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        db_table = 'order'
        verbose_name = '注文'
        verbose_name_plural = '注文'
        indexes = [
            models.Index(fields=['session', 'order_number']),
            models.Index(fields=['status', 'ordered_at']),
        ]

    def __str__(self):
        return f"{self.session} - 注文{self.order_number}"


class OrderItem(models.Model):
    """注文明細"""
    STATUS_CHOICES = [
        ('pending', '未調理'),
        ('cooking', '調理中'),
        ('ready', '調理完了'),
        ('served', '提供済み'),
        ('cancelled', 'キャンセル'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='注文')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name='メニュー項目')
    menu_item_name = models.CharField('商品名', max_length=100, help_text='スナップショット')
    unit_price = models.DecimalField('単価', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], help_text='スナップショット')
    quantity = models.IntegerField('数量', validators=[MinValueValidator(1)])
    subtotal = models.DecimalField('小計', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='pending')
    note = models.TextField('備考', blank=True, null=True, help_text='アレルギー対応など')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        db_table = 'order_item'
        verbose_name = '注文明細'
        verbose_name_plural = '注文明細'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.menu_item_name} x {self.quantity}"


class StaffCall(models.Model):
    """店員呼び出し"""
    REASON_CHOICES = [
        ('water', 'お水が欲しい'),
        ('payment', '会計したい'),
        ('question', '質問がある'),
        ('complaint', '苦情・問題'),
        ('other', 'その他'),
    ]

    STATUS_CHOICES = [
        ('pending', '未対応'),
        ('in_progress', '対応中'),
        ('resolved', '解決済み'),
    ]

    session = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name='セッション')
    reason = models.CharField('理由', max_length=20, choices=REASON_CHOICES)
    message = models.TextField('メッセージ', blank=True, null=True)
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='pending')
    called_at = models.DateTimeField('呼び出し日時')
    responded_at = models.DateTimeField('対応開始日時', blank=True, null=True)
    resolved_at = models.DateTimeField('解決日時', blank=True, null=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        db_table = 'staff_call'
        verbose_name = '店員呼び出し'
        verbose_name_plural = '店員呼び出し'
        indexes = [
            models.Index(fields=['session', 'status']),
            models.Index(fields=['called_at']),
        ]

    def __str__(self):
        return f"{self.session} - {self.get_reason_display()}"


class Payment(models.Model):
    """会計"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', '現金'),
        ('credit_card', 'クレジットカード'),
        ('electronic', '電子マネー'),
    ]

    STATUS_CHOICES = [
        ('pending', '会計待ち'),
        ('paid', '支払済み'),
        ('cancelled', 'キャンセル'),
    ]

    session = models.OneToOneField(Session, on_delete=models.CASCADE, verbose_name='セッション')
    total_amount = models.DecimalField('合計金額', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    payment_method = models.CharField('支払い方法', max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField('会計依頼日時')
    paid_at = models.DateTimeField('支払完了日時', blank=True, null=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        db_table = 'payment'
        verbose_name = '会計'
        verbose_name_plural = '会計'
        indexes = [
            models.Index(fields=['status', 'requested_at']),
        ]

    def __str__(self):
        return f"{self.session} - ¥{self.total_amount}"


class User(AbstractUser):
    """ユーザー/店舗スタッフ"""
    ROLE_CHOICES = [
        ('admin', '管理者'),
        ('chef', '料理人'),
        ('supervisor', 'スーパーバイザ'),
        ('staff', 'スタッフ'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店舗')
    role = models.CharField('役割', max_length=20, choices=ROLE_CHOICES)
    last_login_at = models.DateTimeField('最終ログイン日時', blank=True, null=True)

    class Meta:
        db_table = 'user'
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'
        indexes = [
            models.Index(fields=['store', 'role']),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
