from django.urls import path,include
from .views import OfficeStaffRegistrationView,OfficeUserViewSet,DeliveryStaffRegistrationView,HubDistanceView,DeliveryStaffViewSet,StaffViewSet,HubDash
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'officestaff', OfficeUserViewSet)
router.register(r'deliverystaff', DeliveryStaffViewSet)
router.register(r'staff', StaffViewSet)

    


urlpatterns = [ 
    path('register/officestaff/', OfficeStaffRegistrationView.as_view()),
    path('register/deliverystaff/', DeliveryStaffRegistrationView.as_view()),
    path('oderdistance/', HubDistanceView.as_view()),
    path('dash/', HubDash.as_view()),
    path('', include(router.urls)),
]