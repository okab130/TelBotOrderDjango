from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Store, Table, Category, MenuItem, MenuItemImage,
    Session, Order, OrderItem, StaffCall, Payment, User
)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'phone']


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'store', 'capacity', 'is_available', 'created_at']
    list_filter = ['store', 'is_available', 'created_at']
    search_fields = ['table_number', 'qr_code_url']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'display_order', 'is_active', 'created_at']
    list_filter = ['store', 'is_active', 'created_at']
    search_fields = ['name']
    ordering = ['store', 'display_order']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'is_active', 'display_order', 'created_at']
    list_filter = ['store', 'category', 'is_available', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['store', 'category', 'display_order']


@admin.register(MenuItemImage)
class MenuItemImageAdmin(admin.ModelAdmin):
    list_display = ['menu_item', 'image_type', 'width', 'height', 'file_size', 'uploaded_at']
    list_filter = ['image_type', 'uploaded_at']
    search_fields = ['menu_item__name']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_code', 'table', 'party_size', 'status', 'started_at', 'ended_at']
    list_filter = ['store', 'table', 'status', 'started_at']
    search_fields = ['session_code', 'telegram_chat_id']
    readonly_fields = ['session_code', 'created_at', 'updated_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['menu_item_name', 'unit_price', 'quantity', 'subtotal', 'status']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'order_number', 'total_amount', 'status', 'ordered_at']
    list_filter = ['status', 'ordered_at', 'session__store']
    search_fields = ['telegram_username', 'session__session_code']
    readonly_fields = ['total_amount', 'ordered_at', 'created_at', 'updated_at']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_item_name', 'quantity', 'unit_price', 'subtotal', 'status']
    list_filter = ['status', 'created_at']
    search_fields = ['menu_item_name', 'order__session__session_code']
    readonly_fields = ['menu_item_name', 'unit_price', 'subtotal']


@admin.register(StaffCall)
class StaffCallAdmin(admin.ModelAdmin):
    list_display = ['session', 'reason', 'status', 'called_at', 'responded_at', 'resolved_at']
    list_filter = ['reason', 'status', 'called_at']
    search_fields = ['session__session_code', 'message']
    readonly_fields = ['called_at', 'created_at', 'updated_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['session', 'total_amount', 'payment_method', 'status', 'requested_at', 'paid_at']
    list_filter = ['status', 'payment_method', 'requested_at']
    search_fields = ['session__session_code']
    readonly_fields = ['total_amount', 'requested_at', 'created_at', 'updated_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'store', 'role', 'is_active', 'is_staff']
    list_filter = ['store', 'role', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('店舗情報', {'fields': ('store', 'role', 'last_login_at')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('店舗情報', {'fields': ('store', 'role')}),
    )
