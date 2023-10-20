from django.urls import path
from users.views import RegistrationView,RegisterHandler,ForgetpasswordHandler,Forgetpassword,ResendOtp

urlpatterns = [
    path('userverify/',RegisterHandler.as_view()),
    path('register/', RegistrationView.as_view()),
    path('forget/', ForgetpasswordHandler.as_view()),
    path('forget/change/', Forgetpassword.as_view()),
    path('resend/', ResendOtp.as_view()),
    
    
    
]