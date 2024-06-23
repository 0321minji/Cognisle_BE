from django.urls import path
from .views import *

app_name = "lands"

urlpatterns=[
    path('create/',LandCreateApi.as_view(),name='create'),
    path('item/img/create/',ItemImageCreateApi.as_view(),name='item_img_create'),
    path('show/',ItemShowUpdateApi.as_view(),name='item_show'),
    path('<int:user_id>/',UserLandItemListApi.as_view(),name='lands_items'),
    path('item/update/',ItemLocationUpdateApi.as_view(),name='item_update'),
    path('item/create/',ItemCreateApi.as_view(),name='item_create'),
]