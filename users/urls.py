from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import UserSignUpApi, UserLoginApi,UserDetailApi
app_name = "users"

urlpatterns =[
    path('sign_up/',UserSignUpApi.as_view(),name='sign_up'),
    path('login/',UserLoginApi.as_view(),name='login'),       
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('<int:user_pk>/',UserDetailApi.as_view(),name='detail'),
]