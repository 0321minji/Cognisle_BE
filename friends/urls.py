from django.urls import path
from .views import *

app_name = "friends"

urlpatterns=[
    path('',FriendApi.as_view(),name='friends'),
    path('request/accept/',AcceptRequestApi.as_view(),name='request_accept'),
    path('request/reject/',RejectRequestApi.as_view(),name='request_reject'),
    
]