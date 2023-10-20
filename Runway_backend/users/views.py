from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView, ListAPIView,ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
# from users.models import Users
from django.contrib.auth import authenticate
from users.serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from  auths.utilties import genarate_otp
from rest_framework import viewsets
from auths.models import CustomUser
from users.serializers import UserSerializer
# from auths.utilties import genarate_otp
from datetime import datetime

class RegisterHandler(APIView):
    """Handle creating new user"""

    def post(self, request):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            return Response({"detail": "Active account found in the given credentials"}, status=status.HTTP_401_UNAUTHORIZED)
 
        except Exception as e:
            otp = genarate_otp(email)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            response_data = {
                "otp": otp,
                "time": current_time
            }
            return Response({"data":response_data}, status=status.HTTP_200_OK)
class ResendOtp(APIView):
    def post(self, request):
        email = request.data.get('email')
        
        try:
            user = CustomUser.objects.get(email=email)
            return Response({"message": "Active account found in the given credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            otp = genarate_otp(email)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            response_data = {
                "otp": otp,
                "time": current_time
            }
            return Response({"data":response_data}, status=status.HTTP_200_OK)
class ForgetpasswordHandler(APIView):
    """Handle forget password of user"""

    def post(self, request):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            # return Response({"detail": "Active account found in the given credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            otp = genarate_otp(email)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            response_data = {
                "otp": otp,
                "time": current_time
            }
            return Response({"data":response_data}, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"message": "no Active account found in the given credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
class Forgetpassword(APIView):
    """Handle forget password of user"""

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = CustomUser.objects.get(email=email)
            # return Response({"detail": "Active account found in the given credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            # otp = genarate_otp(email)
            user.set_password(password)
            user.save()
            return Response(status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"message": "no Active account found in the given credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class RegistrationView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # Save the user instance

        # Generate token
        refresh = RefreshToken.for_user(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
            'role':'user'
        }
        return Response(data, status=status.HTTP_200_OK)

