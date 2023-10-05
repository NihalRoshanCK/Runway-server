from django.urls import path, include
from rest_framework.routers import DefaultRouter
from socketSystem.views import NotificationViewSet,MessageViewSet
router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)
router.register(r'message', MessageViewSet)


urlpatterns = [
    path('', include(router.urls)),
]