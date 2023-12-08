"""
URL configuration for Runway_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView 
# from rest_framework.schemas import get_schema_view
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
schema_view = get_schema_view(
    openapi.Info(
        title="Runway",
        default_version="v1",
        description="Runway Api Docs",
        contact=openapi.Contact(email="nihalroshan55@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include("users.urls")),
    path('api-auth/', include('rest_framework.urls')),
    path('admins/',include("admins.urls")),
    path('staff/',include("office_staff.urls")),
    path('delevery/',include("delivery_staff.urls")),
    path('hub/',include("hubs.urls")),
    path('auths/',include("auths.urls")),
    path('product/',include("product.urls")),
    path('sockets/',include("socketSystem.urls")),
    path('openapi/', schema_view.as_view(), name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='swagger-ui'),
    
    path('', TemplateView.as_view(
        template_name='redoc.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='redoc'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
