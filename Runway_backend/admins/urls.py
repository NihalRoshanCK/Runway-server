from django.urls import path,include
from admins.views import HubViewSet,HubAdminRegistrationView,HubAdminViewSet,AdminDash
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'hubhead', HubAdminViewSet)
router.register(r'hub', HubViewSet)


urlpatterns = [
    # path('hubs/', HubViewSet.as_view({'get': 'list', 'post': 'create'}), name='hub-list'),
    # path('hubs/<int:pk>/', HubViewSet.as_view({'get': 'retrieve', 'put': 'update','patch': 'partial_update', 'delete': 'destroy'}), name='hub-detail'),
    path('register/hubadmin/', HubAdminRegistrationView.as_view()),
    path('', include(router.urls)),
    path('admindash/',AdminDash.as_view())
]