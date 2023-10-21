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
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import check_password,make_password

        
class CombinedUserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')

        if email and password and role:
            try:
                if role == 'admin':
                    try:        
                        user = CustomUser.objects.get(email=email, is_superuser=True)
                        if not user.is_active:
                            return Response({"message": "Your account has been deactivated by admin"},status=status.HTTP_403_FORBIDDEN)
                    except:
                        return Response({"message":"Invalid Credentials"},status=status.HTTP_401_UNAUTHORIZED)
                elif role == 'hub_admin':
                    try:
                        
                        user = CustomUser.objects.get(email=email, is_staff=True)
                        if not user.is_active:
                            return Response({"message": "Your account has been deactivated by admin"},status=status.HTTP_403_FORBIDDEN)
                        staff=user.staff
                    # user["is_hubadmin"]=True
                    # user["is_officestaff"]=False
                    # user["is_deleverystaff"]=False
                    except:
                        return Response({"message":"Invalid Credentials"},status=status.HTTP_401_UNAUTHORIZED)
                    if not staff.is_hubadmin:
                        return Response({"message":"Invalid Credentials"},status=status.HTTP_401_UNAUTHORIZED)
                        # raise PermissionDenied("You don't have permission to perform this action.")
                elif role == 'office_staff':
                    try:
                        user = CustomUser.objects.get(email=email, is_staff=True)
                        if not user.is_active:
                            return Response({"message": "Your account has been deactivated by admin"},status=status.HTTP_403_FORBIDDEN)
                        staff=user.staff
                    except:
                        return Response({"message":"Invalid Credentials"},status=status.HTTP_401_UNAUTHORIZED) 
                    if not staff.is_officeStaff:
                        return Response({"message":"Invalid Credentials"},status=status.HTTP_401_UNAUTHORIZED) 
                        # raise PermissionDenied("You don't have permission to perform this action.")
                elif role == 'delivery_staff':
                    try:
                        user = CustomUser.objects.get(email=email, is_staff=True)
                        if not user.is_active:
                            return Response({"message": "Your account has been deactivated by admin"},status=status.HTTP_403_FORBIDDEN)
                        staff=user.staff
                    except:
                        return Response({"message":"Invalid Credentials"},status=status.HTTP_401_UNAUTHORIZED) 
                        
                    if not staff.is_deleverystaff:
                        return Response({"message":"Invalid Credentials"},status=status.HTTP_401_UNAUTHORIZED) 

                else:
                    # return Response({'message': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)
                    user=CustomUser.objects.get(email=email)
                    if not user.is_active:
                            return Response({"message": "Your account has been deactivated by admin"},status=status.HTTP_403_FORBIDDEN)
                    
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
            data = request.data

            # Check if 'password' is in the request data
            if 'new_password' in data and instance==request.user:
                # Check if 'current_password' is in the request data
                if 'current_password' not in data:
                    raise ValidationError("Current password is required to change the password.")

                # Check if the provided current password is correct
                if not check_password(data['current_password'], instance.password):
                    return Response({'detail': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
                # Update the user's password with the new password
                instance.set_password(data['new_password'])
                instance.save()

            return super().partial_update(request, *args, **kwargs)
        else:
            raise ValidationError("You are not allowed to update this user's data.")
    @action(detail=False, methods=['GET'])
    def get_users(self, request):
        queryset = self.get_queryset().filter(is_staff=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)