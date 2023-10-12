# Login view for every modules
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import generics, status
from rest_framework.response import Response
from .utilties import genarate_otp
from auths.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from auths.serializer import UserSerializer
from auths.models import Staff
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import action


        
class CombinedUserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')

        if email and password and role:
            try:
                if role == 'admin':
                    user = CustomUser.objects.filter(email=email, is_superuser=True).first()
                elif role == 'hub_admin':
                    user = CustomUser.objects.get(email=email, is_staff=True)
                    staff=user.staff
                    # user["is_hubadmin"]=True
                    # user["is_officestaff"]=False
                    # user["is_deleverystaff"]=False
                    
                    if not staff.is_hubadmin:
                        raise PermissionDenied("You don't have permission to perform this action.")
                elif role == 'office_staff':
                    user = CustomUser.objects.get(email=email, is_staff=True)
                    staff=user.staff
                    # user["is_hubadmin"]=False
                    # user["is_officestaff"]=True
                    # user["is_deleverystaff"]=False
                    if not staff.is_officeStaff:
                        raise PermissionDenied("You don't have permission to perform this action.")
                elif role == 'delivery_staff':
                    user = CustomUser.objects.get(email=email, is_staff=True)
                    staff=user.staff
                    # user["is_hubadmin"]=False
                    # user["is_officestaff"]=False
                    # user["is_deleverystaff"]=True
                    if not staff.is_deleverystaff:
                        raise PermissionDenied("You don't have permission to perform this action.")
                else:
                    # return Response({'message': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)
                    user=CustomUser.objects.get(email=email)
                    # user["is_hubadmin"]=False
                    # user["is_officestaff"]=False
                    # user["is_deleverystaff"]=False
                if user.check_password(password):
                    refresh = RefreshToken.for_user(user)
                    user_serializer = UserSerializer(user)
                    data = {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        "user":user_serializer.data
                        }
                    data['access_token_payload'] = {
                    'role': role
                    }
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid credentials or not authorized to log in as {}.'.format(role)}, status=status.HTTP_401_UNAUTHORIZED)
            except CustomUser.DoesNotExist:
                return Response({'message': 'User does not exist or is not authorized as {}.'.format(role)}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'Email, password, and role are required.'}, status=status.HTTP_400_BAD_REQUEST)
        

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['partial_update', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action == 'create':
            return [AllowAny()]
        else:
            return [IsAdminUser()]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if the current user is the owner of the instance or an admin
        if instance == request.user or request.user.is_superuser:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            raise ValidationError("You are not allowed to retrieve this user's data.")
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if the current user is the owner of the instance or an admin
        if instance == request.user or request.user.is_superuser:
            return super().partial_update(request, *args, **kwargs)
        else:
            raise ValidationError("You are not allowed to update this user's data.")
    @action(detail=False, methods=['GET'])
    def get_users(self, request):
        queryset = self.get_queryset().filter(is_staff=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)