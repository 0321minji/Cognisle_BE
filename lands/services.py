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
    def create(self, background:str)->Land:
        land_service=LandService()
        land=land_service.create(
            background=background,
            user=self.user
        )
    
        if land is not None:
            return land

class LandService:
    def __init__(self):
        pass
    
    @staticmethod
    def create(background:str,user:User):
        
        land=Land(
            background=background,
            user=user
        )
        
        land.full_clean()
        land.save()
        
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
        
        print(image.image.url)
        return (f'{settings.MEDIA_URL}{image.image.name}', image.pk)

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
            # location 값이 없으면 기본값 설정
            if not item.locations.exists():
                default_location = {'x': '30', 'y': '30', 'z': '3'}
                Location.objects.create(item=item, **default_location)
            return True
    
    @staticmethod
    def create(image_id:str,show=bool):
        item_image=get_object_or_404(ItemImage, pk=image_id)
        print(item_image.image.url)
        # land=get_object_or_404(Land,user=user)
        item=Item(
            item_image=item_image,
            show=show,
            # land=land,
            # user=user,
        )
        item.full_clean()
        item.save()
        
        return item