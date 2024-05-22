from django.db import models
from django.conf import settings

def get_item_pic_upload_path(instance,filename):
    return 'land/item/pic/{}'.format(filename)

class Location(models.Model):
    x=models.CharField(max_length=100,blank=False)
    y=models.CharField(max_length=100,blank=False)
    z=models.CharField(max_length=100,blank=False)
    item=models.ForeignKey('Item',related_name='locations',on_delete=models.SET_NULL, null=True, blank=False)

    
class Item(models.Model):
    image=models.ImageField(upload_to=get_item_pic_upload_path,default='item_pic.png')
    show=models.BooleanField(default=False)

class Land(models.Model):
    #섬 타입(배경), 아이템(27가지:선택된 이미지에 대한 url과 (x,y,z)), 섬 주인(유저)
    background=models.CharField(max_length=10,default=1)    
    landlord=models.ForeignKey('users.User',related_name='lands',on_delete=models.SET_NULL, null=True, blank=False)
    items=models.ManyToManyField('Item',related_name='lands',blank=True)