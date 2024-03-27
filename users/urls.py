from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import UserSignUpApi, SendAPI, VerifyAPI
app_name = "users"

urlpatterns =[
    path('sign_up/',UserSignUpApi.as_view(),name='sign_up'),
    path('send/',SendAPI.as_view(),name='send_sms'),
    path('verify/',VerifyAPI.as_view(),name='verify'),
]