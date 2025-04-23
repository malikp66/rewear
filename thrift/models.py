from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator


User = get_user_model()

phone_regex = RegexValidator(
    regex=r'^(?:\+62|62|0)8[1-9][0-9]{6,9}$',
    message="Masukkan nomor yang valid: contoh 081234567890 atau +6281234567890"
)


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=255)
    full_address = models.TextField()
    notes = models.CharField(max_length=255, blank=True, null=True)
    recipient_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=15,
        unique=True,
        help_text="Format yang diterima: 081234567890, 6281234567890, atau +6281234567890"
    )

    def __str__(self):
        return f"Address of {self.user.username}"

class Product(models.Model):
    CATEGORY_GENDER_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
    ]
    CATEGORY_CHOICES = [
        ("top", "Top"),
        ("bottom", "Bottom"),
        ("outer", "Outer"),
        ("sports", "Sports"),
        ("skirts", "Skirts"),
        ("dress", "Dress"),
        ("hats", "Hats"),
        ("accesories", "Accesories"),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to="products/")
    size = models.CharField(max_length=4)
    color = models.CharField(max_length=50)
    category_gender = models.CharField(max_length=10, choices=CATEGORY_GENDER_CHOICES)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0.00)]
    )
    discount = models.PositiveSmallIntegerField(default=0,validators=[MaxValueValidator(100)], null=True, blank=True)
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Promo(models.Model):
    CATEGORY_CHOICES = [
        ("free_delivery", "Free Delivery"),
        ("discount", "Discount"),
        ("cashback", "Cashback"),
    ]
    CATEGORY_SALES_CHOICES =[
        ("woman", "Woman's Sales"),
        ("man", "Man's Sales"),
        ("fashion", "Fashion's Sales"),
        ("free_delivery", "Free Delivery"),
    ]

    code = models.CharField(max_length=20, unique=True) 
    title = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    category_sales = models.CharField(max_length=20, choices=CATEGORY_SALES_CHOICES)
    discount_percentage = models.FloatField(null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    expiry_date = models.DateTimeField()  
    is_active = models.BooleanField(default=True) 

    def is_valid(self):
        return self.is_active and self.expiry_date > datetime.now()
    
    def __str__(self):
        return self.code

class Order(models.Model):
    STATUS_CHOICES = [
        ("packaging", "Packaging"),
        ("tranship", "Tranship"),
        ("completed", "Completed"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("gopay", "Gopay"),
        ("ovo", "Ovo"),
        ("dana", "Dana"),
        ("cod", "Cash On Delivery"),
        ("credit", "Credit/Card Bank"),
        ("bank", "BCA"),
        ("va", "Virtual Account"),
    ]

    code = models.CharField(max_length=255, blank=True, null=True, unique=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="packaging")
    total_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0.00)]
    )
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=False)
    notes = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    promo = models.ForeignKey(Promo, on_delete=models.SET_NULL, null=True, blank=True) 
    final_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0.00)]
    ) 

    def apply_promo(self):
        if self.promo and self.promo.is_valid():
            if self.promo.discount_percentage:
                discount = (self.total_price * self.promo.discount_percentage) / 100
                if self.promo.max_discount:
                    discount = min(discount, self.promo.max_discount)
            elif self.promo.discount_amount:
                discount = self.promo.discount_amount
            else:
                discount = 0
            self.final_amount = max(self.total_price - discount, 0)  
        else:
            self.final_amount = self.total_price

    def generate_order_code(self):
        first_item = self.items.first()
        if not first_item:
            return "UNKNOWN"

        product = first_item.product
        gender = product.category_gender.upper()[:3]  
        category = product.category.upper()[:3]       
        payment = self.payment_method.upper()[:3]     

        total_orders = Order.objects.count() + 1
        sequence = str(total_orders).zfill(5)         

        return f"{gender}-{category}-{payment}-{sequence}"

    def save(self, *args, **kwargs):
        # if not self.kode:
        #     self.kode = self.generate_order_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order for {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.order.customer.username}"
    
class Review(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review of {self.order} from {self.sender.username}"

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    refund = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Wallet of {self.user.username} that have balance {self.balance}"
    
class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="senders")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receivers")
    message = models.TextField(null=True, blank=True)
    image_message = models.ImageField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message for {self.receiver.username} from {self.sender.username}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # berubah jadi False setelah checkout/kosong

    def add_to_cart(user, product, qty):
        cart, created = Cart.objects.get_or_create(user=user, is_active=True)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += qty
        else:
            cart_item.quantity = qty

        cart_item.save()
    
    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total_price(self):
        return sum(item.get_subtotal() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products')
    quantity = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        return self.product.price

    def __str__(self):
        return f"{self.product.name} x {self.product.price}"
    