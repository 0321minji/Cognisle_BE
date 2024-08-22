from django.urls import path
from .views import *

app_name = "friends"

urlpatterns=[
    path('',FriendApi.as_view(),name='friends'),
]