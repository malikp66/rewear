from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
import string
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    is_seller = models.BooleanField(default=False)  
    store_name = models.CharField(max_length=255, null=True, blank=True)
    store_phone_number = models.CharField(
        max_length=20, null=True, blank=True,
        validators=[RegexValidator(r'^(?:\+62|62|0)8[1-9][0-9]{6,9}$', 'Nomor telepon tidak valid.')]
    )
    npwp = models.CharField(max_length=20, null=True, blank=True)
    address_store = models.TextField(null=True, blank=True)
    province = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    subdistrict = models.CharField(max_length=100, null=True, blank=True)
    store_owner_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(
        max_length=20, null=True, blank=True,
        validators=[RegexValidator(r'^(?:\+62|62|0)8[1-9][0-9]{6,9}$', 'Nomor telepon tidak valid.')]
    )
    nik = models.CharField(max_length=16, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    bank_account_number = models.CharField(max_length=50, null=True, blank=True)
    bank_account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.username

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    otp = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def generate_otp(self):
        """Generate a random OTP of 6 digits."""
        self.otp = ''.join(random.choices(string.digits, k=5))
        self.expires_at = self.created_at + timedelta(minutes=10)  # OTP valid for 10 minutes

    def is_valid(self):
        """Check if OTP is valid and not expired."""
        if self.expires_at is None:
            return False  # Jika expires_at tidak diatur, anggap OTP tidak valid
        return self.expires_at > timezone.now()

    def __str__(self):
        return f"OTP for {self.user.email}"