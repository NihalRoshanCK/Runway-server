from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet,BookingViewSet,PaymentViewSet,OrderViewSet,WorksheetViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'booking', BookingViewSet)
router.register(r'payment',PaymentViewSet)
router.register(r'order',OrderViewSet)
router.register(r'worksheet',WorksheetViewSet)


urlpatterns = [
    path('', include(router.urls)),
    
]






