from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddressViewSet, ProductViewSet, PromoViewSet, OrderViewSet, OrderItemViewSet, ReviewViewSet, WalletViewSet, ChatViewSet, CartViewSet, CartItemViewSet

router = DefaultRouter()
router.register(r'addresses', AddressViewSet)
router.register(r'products', ProductViewSet)
router.register(r'promos', PromoViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'wallets', WalletViewSet)
router.register(r'chats', ChatViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
