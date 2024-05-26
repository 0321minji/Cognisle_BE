from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404

from .models import Land,Location,Item
from users.models import User

class LandCoordinatorService:
    def __init__(self,user:User):
        self.user=user
    
    @transaction.atomic
    def create(self, background:str,items:list[str])->Land:
        land_service=LandService()
        
        land=land_service.create(
            landlord=self.user,
            
            background=background,
            items=items,
        )
    
        if land is not None:
            return land

class LandService:
    def __init__(self):
        pass
    
    @staticmethod
    def create(background:str,items:list[str],landlord:User):
        items=Item.objects.filter(id__in=items)
        
        land=Land(
            background=background,
            landlord=landlord
        )
        
        land.full_clean()
        land.save()
        
        land.items.set(items)
        return land