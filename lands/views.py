from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers, status
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)
from users.models import User
from .selectors import ItemSelector, LandSelector
from rest_framework.exceptions import PermissionDenied
from .models import Land, Location, Item, ItemImage
from .services import LandCoordinatorService, ItemImageService, ItemService
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
class LandCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class LandCreateInputSerializer(serializers.Serializer):
        background=serializers.CharField(required=False,default=1)
        user_id=serializers.CharField(required=False)
    @swagger_auto_schema(
        request_body=LandCreateInputSerializer,
        security=[],
        operation_id='Land 생성 API',
        operation_description="기본 섬 생성 API.\n 회원가입시 함께 사용 or 서버가 직접 사용",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                        "data":{'id':1},
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )    
      
    def post(self,request):
        serializers=self.LandCreateInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data=serializers.validated_data
        
        service=LandCoordinatorService(user=request.user)
        
        land=service.create(
            background=data.get('background'),
            user_id=data.get('user_id')
        )
        
        if land:
            return Response({
                'status' : 'success',
                'data' : {'id': land.id},
            },status=status.HTTP_201_CREATED)
        else:
            return Response({
                'status': 'error',
                'message': 'Failed to create land.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
class ItemImageCreateApi(APIView):
    permission_classes=(IsAuthenticated,)
    
    class ItemImageCreateInputSerializer(serializers.Serializer):
        image=serializers.ImageField()
    
    @swagger_auto_schema(
        request_body=ItemImageCreateInputSerializer,
        security=[],
        operation_id='아이템 이미지 생성 API',
        operation_description="아이템 이미지를 생성하는 API 입니다.",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                        "data":{'img_pk':'1',
                                'url':'https://s3.ap-northeast-2.amazonaws.com/cognisle.shop/media/lands/item/pic/1717246454.20869859d06b930207a43f38b444c80139a66a6.jpg'}
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )    
    
    def post(self,request):
        serializer=self.ItemImageCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=serializer.validated_data
        
        item_img_url,image_pk=ItemImageService.create( 
            image=data.get('image'),
        )
        
        return Response({
            'status':'success',
            'data':{'img_pk':image_pk,
                'url':item_img_url},
        },status=status.HTTP_201_CREATED)

class ItemCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class ItemCreateInputSerializer(serializers.Serializer):
        image_id = serializers.CharField()
    class LocationUpdateInputSerializer(serializers.Serializer):
        item_id = serializers.IntegerField()
        x = serializers.CharField(max_length=100)
        y = serializers.CharField(max_length=100)
        z = serializers.CharField(max_length=100)

    class MultipleLocationUpdateSerializer(serializers.Serializer):
        locations = serializers.ListField(child=serializers.DictField(),required=False)
        land_back_id = serializers.IntegerField(required=False, allow_null=True)

    @swagger_auto_schema(
        request_body=ItemCreateInputSerializer,
        security=[],
        operation_id='아이템 생성 API',
        operation_description="아이템을 생성하는 API",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                        "data":{
                            'item_pk':'2',
                            'item_image':'https://s3.amazonaws.com/cognisle.shop/media/lands/background/land2',
                            'item_show':'false',
                        }
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )    
    
    def post(self,request):
        serializer=self.ItemCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=serializer.validated_data
        
        item=ItemService.create(
            image_id=data.get('image_id'),
            # user=request.user,
        )
        
        print(item.item_image)
        return Response({
            'status':'success',
            'data':{
                'item_pk':item.pk,
                'item_image':item.item_image.image,
            }
        })

    @swagger_auto_schema(
        request_body=MultipleLocationUpdateSerializer,
        security=[],
        operation_id='아이템 위치 변경 API',
        operation_description="섬꾸미기를 통한 아이템들의 변경된 위치들을 받아서 변경하는 API",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                        "data":{
                            'updated_items': [{
                                'id': 2,
                                'locations': {
                                    'x': 20,
                                    'y': 30,
                                    'z': 5
                                }
                            },{
                                'id': 5,
                                'locations': {
                                    'x': 44,
                                    'y': 30,
                                    'z': 4
                                }
                            }
                                              
                            ],
                            'land_background_id':1,
                        }
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )    
    
    @transaction.atomic
    def put(self, request):
        serializer = self.MultipleLocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        land_back_id=data.get('land_back_id')
        locations_data = data.get('locations',[])
        
        print(f"Land back ID: {land_back_id}")
        for location_data in locations_data:
            item = get_object_or_404(Item, pk=location_data['item_id'])
            user_emails = item.users.values_list('email', flat=True)
            print(user_emails,request.user)
            if request.user in user_emails:
                raise PermissionDenied(f"You do not have permission to update the location of item {item.id}.")

            # 기존 위치 정보를 가져오거나 생성합니다.
            location, created = Location.objects.get_or_create(item=item,land=request.user.lands)
            
            # 위치 정보를 업데이트합니다.
            location.x = location_data['x']
            location.y = location_data['y']
            location.z = location_data['z']
            location.save()
                
            if created:
                item.show=True
                item.save()
            
        if land_back_id:
            land = get_object_or_404(Land,user=request.user)
            if request.user !=land.user:
                raise PermissionDenied(f"You do not have permission to update the land of {land.user}.")
            land.background=land_back_id 
            land.save()
            
        return Response({
            'status': 'success',
            'data': {
                'updated_items': [{
                    'id': location_data['item_id'],
                    'locations': {
                        'x': location_data['x'],
                        'y': location_data['y'],
                        'z': location_data['z']
                    }
                } for location_data in locations_data],
                'land_background_id':land_back_id,
            }
        }, status=status.HTTP_200_OK)    
        
#아이템 show 변경 api(사용->사용X시)
class ItemShowUpdateApi(APIView):
    permission_classes=(IsAuthenticated,)
    
    class ItemShowUpdateSerializer(serializers.Serializer):
        item_id = serializers.IntegerField()
        
    @swagger_auto_schema(
        request_body=ItemShowUpdateSerializer,
        security=[],
        operation_id='아이템 사용여부 변경 API',
        operation_description="아이템을 사용하거나 사용해제하는 API",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                        "data":{
                            'item_show':'true',
                        }
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )    
    def post(self, request, *args, **kwargs):
        serializer = self.ItemShowUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        item_id=data.get('item_id')
        item = get_object_or_404(Item, pk=item_id)
        # 현재 로그인한 유저가 해당 아이템의 소유자인지 확인
        if item.user != request.user:
            raise PermissionDenied("You do not have permission to update this item.")
        
        shows = ItemService.show_or_no(item=item)
        
        return Response({
            'status':'success',
            'data':{'show':shows},
        },status=status.HTTP_200_OK)


class UserLandItemListApi(APIView):
    permission_classes = (IsAuthenticated,)

    class ItemImageSerializer(serializers.Serializer):
        image = serializers.ImageField()

    class LocationSerializer(serializers.Serializer):
        x = serializers.CharField(max_length=100)
        y = serializers.CharField(max_length=100)
        z = serializers.CharField(max_length=100)

    class ItemSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        item_image = serializers.SerializerMethodField()
        locations = serializers.SerializerMethodField()

        def get_item_image(self, obj):
            return obj.item_image.image.url if obj.item_image else None

        def get_locations(self, obj):
            user_id = self.context.get('user_id')
            locations = obj.locations.filter(land__user=user_id)
            return UserLandItemListApi.LocationSerializer(locations, many=True).data
    
    class LandItemOutputSerializer(serializers.Serializer):
        land = serializers.SerializerMethodField()
        items = serializers.SerializerMethodField()

        def get_land(self, obj):
            s3_base_url = "https://s3.ap-northeast-2.amazonaws.com/cognisle.shop/media/lands/background/"
            land_img = f'{s3_base_url}land{obj.background}.png'
            bg_img = f'{s3_base_url}bg{obj.background}.png'
            return {'state': obj.background, 'land_img': land_img, 'bg_img': bg_img}

        def get_items(self, obj):
            request = self.context.get('request')
            items = self.context.get('items')
        
            if obj.user == request.user:
                # 소유자면 모든 아이템 반환
                return UserLandItemListApi.ItemSerializer(items, many=True,context={'user_id':self.context.get('user_id')}).data
            else:
                # 사용된 아이템만 필터링하여 반환
                used_items = []
                for item in items:
                    if item.locations.filter(land=obj, show=True).exists():
                        used_items.append(item)
                return UserLandItemListApi.ItemSerializer(used_items, many=True,context={'user_id':self.context.get('user_id')}).data
            
    @swagger_auto_schema(
        operation_id='아이템 리스트 조회 API',
        operation_description="소유하고 있는 모든 아이템과 섬 상태를 조회하는 API(user=request)",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                        "data":{
                            'user':3,
                            'lands':{
                                "state":"2",
                                "land_img":"https://s3.ap-northeast-2.amazonaws.com/cognisle.shop/media/lands/background/land2",
                                "bg_img": "https://s3.ap-northeast-2.amazonaws.com/cognisle.shop/media/lands/background/bg2"
                            },
                            "items": [
                                {
                                    "id": 1,
                                    "show": 'true',
                                    "item_image": "https://s3.ap-northeast-2.amazonaws.com/cognisle.shop/media/lands/item/pic/KakaoTalk_20240227_203618663.png",
                                    "locations": [
                                        {
                                            "x": "100",
                                            "y": "200",
                                            "z": "300"
                                        }
                                    ]
                                },
                                    {
                                    "id": 2,
                                    "show": 'true',
                                    "item_image": "https://s3.ap-northeast-2.amazonaws.com/cognisle.shop/media/lands/item/pic/1716722334.059527112cbccf5a3a4226aa1a504843bcc4ff.jpg",
                                    "locations": [
                                        {
                                            "x": "400",
                                            "y": "500",
                                            "z": "600"
                                        }
                                    ]   
                                }
                            ]
                        }
                        
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )    
            
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        print(user.email)
        print(request.user.id)
        land = LandSelector.get_user_land(user_id=user_id)
        items=LandSelector.get_user_items(user_id=user_id)
        logger.info(f"Lands and items retrieved: {land}")
        output_serializer = self.LandItemOutputSerializer(land, context={'user_id':user_id,'request': request,'items':items})
        # if request.user.id == user_id:
        #     output_serializer = self.LandItemOutputSerializer(lands_items, many=True)
        # else:
        #     output_serializer = self.PublicLandItemOutputSerializer(lands_items, many=True)
        return Response(
            {'status':'sucess',
             'data':{'owner':user.email,
                     'land':output_serializer.data.get('land'),
                     'items':output_serializer.data.get('items')}}, status=status.HTTP_200_OK)

class ItemLocationUpdateApi(APIView):
    permission_classes = (IsAuthenticated,)
    class LocationUpdateInputSerializer(serializers.Serializer):
        item_id = serializers.IntegerField()
        x = serializers.CharField(max_length=100)
        y = serializers.CharField(max_length=100)
        z = serializers.CharField(max_length=100)

    class MultipleLocationUpdateSerializer(serializers.Serializer):
        locations = serializers.ListField(child=serializers.DictField(),required=False)
        land_back_id = serializers.IntegerField(required=False, allow_null=True)

    @swagger_auto_schema(
        request_body=MultipleLocationUpdateSerializer,
        security=[],
        operation_id='아이템 위치 변경 API',
        operation_description="섬꾸미기를 통한 아이템들의 변경된 위치들을 받아서 변경하는 API",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                        "data":{
                            'updated_items': [{
                                'id': 2,
                                'locations': {
                                    'x': 20,
                                    'y': 30,
                                    'z': 5
                                }
                            },{
                                'id': 5,
                                'locations': {
                                    'x': 44,
                                    'y': 30,
                                    'z': 4
                                }
                            }
                                              
                            ],
                            'land_background_id':1,
                        }
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )    
    
    @transaction.atomic
    def put(self, request):
        serializer = self.MultipleLocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        land_back_id=data.get('land_back_id')
        locations_data = data.get('locations',[])
        
        print(f"Land back ID: {land_back_id}")
        for location_data in locations_data:
            item = get_object_or_404(Item, pk=location_data['item_id'])
            user_emails = item.users.values_list('email', flat=True)
            print(user_emails,request.user)
            if request.user in user_emails:
                raise PermissionDenied(f"You do not have permission to update the location of item {item.id}.")

            # 기존 위치 정보를 가져오거나 생성합니다.
            location, created = Location.objects.get_or_create(item=item,land=request.user.lands)
            
            # 위치 정보를 업데이트합니다.
            location.x = location_data['x']
            location.y = location_data['y']
            location.z = location_data['z']
            location.save()
                
            if created:
                item.show=True
                item.save()
            
        if land_back_id:
            land = get_object_or_404(Land,user=request.user)
            if request.user !=land.user:
                raise PermissionDenied(f"You do not have permission to update the land of {land.user}.")
            land.background=land_back_id 
            land.save()
            
        return Response({
            'status': 'success',
            'data': {
                'updated_items': [{
                    'id': location_data['item_id'],
                    'locations': {
                        'x': location_data['x'],
                        'y': location_data['y'],
                        'z': location_data['z']
                    }
                } for location_data in locations_data],
                'land_background_id':land_back_id,
            }
        }, status=status.HTTP_200_OK)

class ItemGetApi(APIView):
    permission_classes=(IsAuthenticated,)
    
    class ItemGetInputSerializer(serializers.Serializer):
        item_ids = serializers.ListField(child=serializers.IntegerField())
    @swagger_auto_schema(
        request_body=ItemGetInputSerializer,
        security=[],
        operation_id='아이템 획득 API',
        operation_description="게임을 통해 얻은 아이템들 중 새로 획득한 아이템을 저장하는 API",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                        "new_item_ids":[1,5,13]
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )
    @transaction.atomic
    def put(self,request):
        serializers = self.ItemGetInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data=serializers.validated_data
        
        item_ids = data.get('item_ids')
        new_item_ids=[]
        
        for item_id in item_ids:
            item = get_object_or_404(Item,pk=item_id)
            user_emails = item.users.values_list('email', flat=True)
            if request.user not in user_emails:
                item.users.add(request.user)
                item.save()  # 변경 사항 저장
                Location.objects.create(
                    item=item,
                    land=request.user.lands,
                    x=0,y=0,z=0,
                )
                new_item_ids.append(item_id)
        return Response({'status': 'success',
                         'new_item_ids':new_item_ids}, status=200)   

# class ItemImageSerializer(serializers.Serializer):
#     #item
class ItemSerializer(serializers.Serializer):
    item_image = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    
    def get_item_image(self, obj):
        return obj.item_image.image
class ItemListApi(APIView):
    permission_classes=(AllowAny,)
    
    class ItemListOutputSerializer(serializers.Serializer):
        items = ItemSerializer(many=True)
        
    def get(self,request,user_id):
        user=get_object_or_404(User,pk=user_id)
        items=LandSelector.get_user_items(user_id=user_id)
        
        output_serializer=self.ItemListOutputSerializer({'items': items})
        
        return Response({
            'status':'success',
            'data':output_serializer.data
        },status=status.HTTP_200_OK)
