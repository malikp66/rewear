from django.contrib import admin
from .models import Address, Product, Promo, Order, OrderItem, Review, Wallet, Chat, Cart, CartItem


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'recipient_name', 'phone_number')
    search_fields = ('user__username', 'label', 'recipient_name', 'phone_number')
    readonly_fields = ('phone_number',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'is_sold', 'category', 'category_gender')
    search_fields = ('name', 'seller__username', 'category', 'category_gender')
    list_filter = ('is_sold', 'category', 'category_gender')
    readonly_fields = ('is_sold',)


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'category', 'category_sales', 'is_active', 'expiry_date')
    search_fields = ('code', 'title')
    list_filter = ('category', 'category_sales', 'is_active')
    readonly_fields = ('is_active', 'expiry_date')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'status', 'total_price', 'is_paid', 'created_at', 'code')
    search_fields = ('customer__username', 'status', 'code')
    list_filter = ('status', 'is_paid', 'created_at')
    readonly_fields = ('created_at', 'is_paid', 'code')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    search_fields = ('order__customer__username', 'product__name')
    list_filter = ('order', 'product')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('sender', 'product', 'rating', 'created_at')
    search_fields = ('sender__username', 'product__name')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at',)
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'refund', 'profit')
    search_fields = ('user__username',)
    readonly_fields = ('balance', 'refund', 'profit')


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp')
    search_fields = ('sender__username', 'receiver__username')
    readonly_fields = ('timestamp', 'message', 'image_message')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'get_price', 'get_subtotal')
    search_fields = ('cart__user__username', 'product__name')

    def get_price(self, obj):
        return obj.product.price
    get_price.short_description = 'Product Price'

    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'

    readonly_fields = ('get_price', 'get_subtotal')
