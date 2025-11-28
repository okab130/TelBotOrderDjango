from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'stores', views.StoreViewSet)
router.register(r'tables', views.TableViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'menu-items', views.MenuItemViewSet)
router.register(r'sessions', views.SessionViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'order-items', views.OrderItemViewSet)
router.register(r'staff-calls', views.StaffCallViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/telegram/webhook/', views.TelegramWebhookView.as_view(), name='telegram-webhook'),
    path('miniapp/', views.miniapp_view, name='miniapp'),
]
