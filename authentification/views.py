from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from .serializers import RegisterBuyerSerializer, BecomeSellerSerializer, CustomTokenObtainPairSerializer, UserSerializer, SellerDetailSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, filters
from thrift.models import Product, OrderItem
from django.db.models import Avg
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

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

from rest_framework.parsers import JSONParser

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
