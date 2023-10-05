from django.urls import path
from users.views import RegistrationView,RegisterHandler

urlpatterns = [
    path('userverify/',RegisterHandler.as_view()),
    path('register/', RegistrationView.as_view()),
]