from django.urls import path
from .views import *

app_name = "lands"

urlpatterns=[
    path('create/',LandCreateApi.as_view(),name='create'),
    path('item/img/create/',ItemImageCreateApi.as_view(),name='item_img_create'),
]