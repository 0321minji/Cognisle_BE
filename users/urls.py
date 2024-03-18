from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import UserSignUpApi
app_name = "users"

urlpatterns =[
    path('signup/',UserSignUpApi.as_view(),name='signup'),
]