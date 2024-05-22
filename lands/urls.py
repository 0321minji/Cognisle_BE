from django.urls import path
from .views import *

app_name = "lands"

urlpatterns=[
    path('create/',LandCreateApi.as_view(),name='create'),
]