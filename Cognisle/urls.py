"""Cognisle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="Cognisle",
        default_version="v1",
        description="Cognisle BE API",
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path(r'swagger(?P<format>\.json|\.yaml$)/',schema_view.without_ui(cache_timeout=0),name='schema-json'),
    path(r'swagger/',schema_view.with_ui('swagger',cache_timeout=0),name='schema-swagger-ui'),
    path(r'redoc/',schema_view.with_ui('redoc',cache_timeout=0),name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('users/',include('users.urls')),
    path('lands/',include('lands.urls')),
    path('friends/',include('friends.urls')),
    path('gbooks/',include('gbooks.urls')),
]
