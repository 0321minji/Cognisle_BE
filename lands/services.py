from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
import io, time, uuid
from django.conf import settings
from Cognisle.settings import development
from .selectors import ItemSelector
from .models import Land,Location,Item, ItemImage
from users.models import User
from core.utils import s3_file_upload_by_file_data
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from django.db import IntegrityError

class LandCoordinatorService:
    def __init__(self,user:User):
        self.user=user
    
    @transaction.atomic
    def create(self, background:str,user_id:str)->Land:
        land_service=LandService()
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                raise NotFound("해당 ID를 가진 사용자를 찾을 수 없습니다.")
        else:
            # user_id가 제공되지 않으면 요청한 사용자로 설정
            if not self.user.is_authenticated:
                raise PermissionDenied("사용자가 인증되지 않았습니다.")
            user = self.user
        land=land_service.create(
            background=background,
            user=user
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
    def create(image:ImageFile):
        img_url=s3_file_upload_by_file_data(
            upload_file=image,
            region_name=development.AWS_S3_REGION_NAME,
            bucket_name=development.AWS_STORAGE_BUCKET_NAME,
            bucket_path=f'media/lands/item/pic'
        )
        item_image=ItemImage(image=img_url)
        item_image.save()
        print(item_image.image)
        return (item_image.image, item_image.pk)

class ItemService:
    def __init__(self):
        pass
    @staticmethod
    # def show_or_no(item:Item)->bool:
    #     selector=ItemSelector()
    #     if selector.show(item=item):
    #         item.show=False
            
    #         item.full_clean()
    #         item.save()
    #         return False
    #     else:
    #         item.show=True
    #         item.full_clean()
    #         item.save()
    #         # location 값이 없으면 기본값 설정
    #         if not item.locations.exists():
    #             default_location = {'x': '30', 'y': '30', 'z': '3'}
    #             Location.objects.create(item=item, **default_location)
    #         return True
    
    @staticmethod
    def create(image_id:str):
        item_image=get_object_or_404(ItemImage, pk=image_id)
        print(item_image.image)
        try:
            item=Item(
                item_image=item_image,
            )
            item.full_clean()
            item.save()
        except ValidationError as e:
            # ValidationError가 발생하면 예외를 발생시킴
            raise Exception(f"Validation error: {e.message_dict}")
        except IntegrityError as e:
            # 데이터베이스 무결성 오류 발생 시 예외 발생
            raise Exception(f"Integrity error: {str(e)}")
        return item