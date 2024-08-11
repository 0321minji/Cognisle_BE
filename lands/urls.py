from django.urls import path
from .views import *

app_name = "lands"

urlpatterns=[
    path('',LandCreateApi.as_view(),name='create'),
    path('items/img/',ItemImageCreateApi.as_view(),name='item_img_create'),
    #path('show/',ItemShowUpdateApi.as_view(),name='item_show'),
    path('<int:user_id>/',UserLandItemListApi.as_view(),name='lands_items'),
    #path('items/',ItemLocationUpdateApi.as_view(),name='item_update'),
    path('items/',ItemCreateApi.as_view(),name='item_create'),
    path('items/game/',ItemGetApi.as_view(),name='item_get'),
    path('items/<int:user_id>/',ItemListApi.as_view(),name='item_list'),
    #path('items/',AllItemListApi.as_view(),name='all_item_list'),
]