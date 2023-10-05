from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView, ListAPIView,ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from users.serializers import UserSerializer
from admins.serializers import HubSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from hubs.models import Hub
from auths.models import Staff
from rest_framework import viewsets,permissions  
from .serializers import HubSerializer,HubAdminSerializer,HubAdminViewSetSerialize,HubCreationSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser,BasePermission
from auths.utilties import IsHubAdmin
# Create your views here.


# class IsHubAdmin(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.staff.is_hubadmin

# class HubViewSet(viewsets.ModelViewSet):
#     queryset = Hub.objects.all()
#     serializer_class = HubSerializer
#     permission_classes = [IsAuthenticated | IsAdminUser ]    

class HubAdminRegistrationView(CreateAPIView):
    permission_classes = [IsAuthenticated & (IsAdminUser | IsHubAdmin)]
    serializer_class = HubAdminSerializer
    
    def perform_create(self, serializer):
        serializer.save()
        
class HubAdminViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class=HubAdminViewSetSerialize
    
# class HubViewSet(viewsets.ModelViewSet):
#     queryset = Hub.objects.all()
#     serializer_class = HubSerializer
#     permission_classes = [IsAdminUser]
    
    # def create(self, request, *args, **kwargs):
        # Extract hub data from request
    
class HubViewSet(viewsets.ModelViewSet):
    queryset = Hub.objects.all()
    serializer_class = HubCreationSerializer
    permission_classes = [IsAdminUser]