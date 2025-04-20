import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from thrift.models import Product, OrderItem, Review
from django.db.models import Avg

User = get_user_model()

class SellerDetailSerializer(serializers.ModelSerializer):
    total_products_sold = serializers.SerializerMethodField()
    total_rating_from_sold_products = serializers.SerializerMethodField()
    last_online = serializers.SerializerMethodField()
    total_products_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'is_seller', 'profile_pics',
            'store_name', 'store_phone_number', 'npwp', 'address_store',
            'province', 'city', 'subdistrict', 'store_owner_name',
            'phone_number', 'nik', 'bank_name', 'bank_account_number', 
            'bank_account_holder_name', 'last_online', 'total_products_sold',
            'total_rating_from_sold_products', 'total_products_count',
        ]

    def get_total_products_sold(self, obj):
        return OrderItem.objects.filter(product__seller=obj).count()

    def get_total_rating_from_sold_products(self, obj):
        reviews = Review.objects.filter(product__seller=obj)
        rating_avg = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(rating_avg or 0.0, 2)
    
    def get_last_online(self, obj):
        if obj.last_online:
            return obj.last_online.strftime("%Y-%m-%d %H:%M:%S")
        return "Belum pernah online"
    
    def get_total_products_count(self, obj):
        return Product.objects.filter(seller=obj).count()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'is_seller', 'profile_pics', 'store_name', 'store_phone_number',
            'npwp', 'address_store', 'province', 'city', 'subdistrict', 'store_owner_name',
            'phone_number', 'nik', 'bank_name', 'bank_account_number', 'bank_account_holder_name',
        ]
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_seller"] = user.is_seller
        return token
    
    def validate(self, attrs):
        tokens = super().validate(attrs)

        # Atur struktur respons sesuai urutan yang diinginkan
        data = {
            "user": {
                "id": self.user.id,
                "username": self.user.username,
                "email": self.user.email
            },
            "refresh": tokens['refresh'],
            "access": tokens['access']
        }

        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_seller"]

class RegisterBuyerSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        value = ' '.join(value.split())

        if not re.match(r'^[A-Za-z\s]+$', value):
            raise serializers.ValidationError("Username hanya boleh berisi huruf dan spasi, tanpa angka atau simbol.")

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username sudah digunakan. Silakan pilih yang lain.")

        return value
    
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email sudah digunakan. Silakan gunakan email lain.")
        return value    

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password harus memiliki minimal 8 karakter.")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password harus mengandung setidaknya satu huruf kecil.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password harus mengandung setidaknya satu huruf besar.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password harus mengandung setidaknya satu angka.")
        if ' ' in value:
            raise serializers.ValidationError("Password tidak boleh mengandung spasi.")
        
        clean_username = re.sub(r'\s+', '', self.initial_data['username'].lower())
        clean_password = re.sub(r'\s+', '', value.lower())

        if clean_password == clean_username or clean_password == clean_username[::-1]:
            raise serializers.ValidationError("Password tidak boleh sama dengan username atau username terbalik (tanpa spasi).")
                
        return value
    
    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Password tidak cocok, tolong coba lagi")
        return data

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class BecomeSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "store_name", "store_phone_number", "npwp",
            "address_store", "province", "city", "subdistrict", "store_owner_name",
            "phone_number", "nik", "bank_name", "bank_account_number", "bank_account_holder_name",
        ]
        extra_kwargs = {
            "store_name": {"required": True},
            "nik": {"required": True},
            "store_phone_number": {"required": True},
            "bank_account_number": {"required": True},
        }

    def validate_nik(self, value):
        if not re.match(r'^\d{16}$', value):
            raise serializers.ValidationError("NIK harus 16 digit angka.")
        return value


    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.is_seller = True
        instance.save()
        return instance
