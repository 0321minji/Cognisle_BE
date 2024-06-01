from django.db import models
from django.conf import settings

def get_item_pic_upload_path(instance,filename):
    return 'lands/item/pic/{}'.format(filename)

class Location(models.Model):
    x=models.CharField(max_length=100,blank=False)
    y=models.CharField(max_length=100,blank=False)
    z=models.CharField(max_length=100,blank=False)
    item=models.ForeignKey('Item',related_name='locations',on_delete=models.SET_NULL, null=True, blank=False)

#일단 lands 앱 안에 item 모델도 생성하긴 했는데 따로 앱 만드는게 좋을지
class ItemImage(models.Model):
    image = models.ImageField(upload_to=get_item_pic_upload_path, default='item_image.png')
    
class Item(models.Model):
    item_image = models.ForeignKey(ItemImage, on_delete=models.CASCADE, related_name='items')
    show=models.BooleanField(default=False)
    land=models.ForeignKey('Land',related_name='lands',on_delete=models.SET_NULL,null=True)
    user=models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='items')
    
class Land(models.Model):
    #섬 타입(배경), 아이템(27가지:선택된 이미지에 대한 url과 (x,y,z)), 섬 주인(유저)
    background=models.CharField(max_length=10,default=1)    
    user=models.ForeignKey('users.User',related_name='lands',on_delete=models.SET_NULL, null=True, blank=False)