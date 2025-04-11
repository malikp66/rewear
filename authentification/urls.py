from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterBuyerView, BecomeSellerView, CustomTokenObtainPairView

urlpatterns = [
    path("register/buyer/", RegisterBuyerView.as_view(), name="register_buyer"),
    path("register/seller/", BecomeSellerView.as_view(), name="register_seller"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

