from django.urls import path
from .views import *

app_name = "lands"

urlpatterns=[
    path('create/',LandCreateApi.as_view(),name='create'),
    path('item/img/create/',ItemImageCreateApi.as_view(),name='item_img_create'),
    path('<int:item_id>/show/',ItemShowUpdateApi.as_view(),name='item_show'),
    path('<int:user_id>/items/',UserLandItemListApi.as_view(),name='lands_items'),
]