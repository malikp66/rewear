from rest_framework import viewsets
from .models import Address, Product, Promo, Order, OrderItem, Review, Wallet, Chat, Cart, CartItem, Collection
from .serializers import AddressSerializer, ProductSerializer, PromoSerializer, OrderSerializer, OrderItemSerializer, ReviewSerializer, WalletSerializer, ChatSerializer, CartSerializer, CartItemSerializer, CollectionSerializer, CollectionDetailSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class PromoViewSet(viewsets.ModelViewSet):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer

    def get_queryset(self):
        """
        Mengembalikan hanya promo yang aktif jika request adalah 'list'.
        """
        if self.action == 'list':
            return Promo.objects.filter(is_active=True)
        return Promo.objects.all()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
    def get_queryset(self):
        queryset = Cart.objects.all()
        user_id = self.request.query_params.get('user', None)
        is_active = self.request.query_params.get('is_active', None)

        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        queryset = CartItem.objects.all()
        cart_id = self.request.query_params.get('cart', None)
        product_id = self.request.query_params.get('product', None)

        if cart_id is not None:
            queryset = queryset.filter(cart_id=cart_id)
        if product_id is not None:
            queryset = queryset.filter(product_id=product_id)

        return queryset
    
class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CollectionDetailSerializer
        return CollectionSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Collection.objects.filter(user=self.request.user)
        return Collection.objects.none()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        products = request.data.get('products', None)

        if products is not None:
            # Cuma update products
            instance.products.set(products)
            instance.save()

            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return super().partial_update(request, *args, **kwargs)