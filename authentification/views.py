from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import RegisterBuyerSerializer, BecomeSellerSerializer, CustomTokenObtainPairSerializer, UserSerializer, SellerDetailSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, filters

User = get_user_model()

class SellerListView(generics.ListAPIView):
    queryset = User.objects.filter(is_seller=True)
    serializer_class = SellerDetailSerializer
    permission_classes = [AllowAny] 
    filter_backends = [filters.SearchFilter]
    search_fields = ['store_name']

class UserDetailView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

class RegisterBuyerView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterBuyerSerializer
    permission_classes = [permissions.AllowAny]

class BecomeSellerView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
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
