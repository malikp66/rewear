from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from .serializers import RegisterBuyerSerializer, BecomeSellerSerializer, CustomTokenObtainPairSerializer, UserSerializer, SellerDetailSerializer, ForgotPasswordSerializer, VerifyOTPSerializer, ResendOTPSerializer,ResetPasswordSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, filters
from thrift.models import Product, OrderItem
from .models import PasswordResetOTP
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.db.models import Avg
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)
from rest_framework.parsers import JSONParser


User = get_user_model()

class SellerListView(generics.ListAPIView):
    queryset = User.objects.filter(is_seller=True)
    serializer_class = SellerDetailSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['store_name']

class SellerRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.filter(is_seller=True)
    serializer_class = SellerDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        token = request.auth

        if token is None:
            return Response({"error": "No valid token provided"}, status=status.HTTP_401_UNAUTHORIZED)

        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_seller': user.is_seller,
        }

        return Response(user_data)

    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RegisterBuyerView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterBuyerSerializer
    permission_classes = [permissions.AllowAny]

class BecomeSellerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    #Atau kalau udah nggak error lagi bisa mintol ganti dua yang atas make ini"""
    # permission_classes = [permissions.allowAny]
    # authentication_classes = [permissions.allowAny]
    
    def patch(self, request):
        logger.info(f"Request headers: {request.headers}")
        logger.info(f"Request user: {request.user}")
        serializer = BecomeSellerSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Akun berhasil di-upgrade menjadi seller.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        return self.patch(request)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Email not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate OTP
        otp_instance = PasswordResetOTP.objects.create(user=user)
        otp_instance.generate_otp()
        otp_instance.save()

        # Send email
        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP code is: {otp_instance.otp}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'message': 'OTP sent to email.'}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email)
            otp_instance = PasswordResetOTP.objects.filter(user=user, otp=otp).last()

            if otp_instance and otp_instance.is_valid():
                return Response({'message': 'OTP is valid.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'error': 'Email not found.'}, status=status.HTTP_404_NOT_FOUND)

class ResendOTPView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Email not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate new OTP
        otp_instance = PasswordResetOTP.objects.create(user=user)
        otp_instance.generate_otp()
        otp_instance.save()

        send_mail(
            subject='Your New OTP Code',
            message=f'Your new OTP code is: {otp_instance.otp}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'message': 'New OTP sent to email.'}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)