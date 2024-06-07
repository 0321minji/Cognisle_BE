from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
import io, time, uuid
from django.conf import settings
from .selectors import ItemSelector
from .models import Land,Location,Item, ItemImage
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
    
class ItemImageService:
    def __init__(self):
        pass
    
    @staticmethod
    def create(image:InMemoryUploadedFile):
        ext=image.name.split(".")[-1]
        file_path='{}.{}'.format(str(time.time())+str(uuid.uuid4().hex),ext)
        img=ImageFile(io.BytesIO(image.read()),name=file_path)
        image=ItemImage(image=img)
        
        image.full_clean()
        image.save()
        
        return settings.MEDIA_URL+image.image.name

class ItemService:
    def __init__(self):
        pass
    @staticmethod
    def show_or_no(item:Item)->bool:
        selector=ItemSelector()
        if selector.show(item=item):
            item.show=False
            
            item.full_clean()
            item.save()
            return False
        else:
            item.show=True
            
            item.full_clean()
            item.save()
            return True
        