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
from lands.models import Location
from .selectors import ItemSelector, LandSelector
from rest_framework.exceptions import PermissionDenied
from .models import Land, Location, Item, ItemImage
from .services import LandCoordinatorService, ItemImageService, ItemService
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
class LandApi(APIView):
    permission_classes=(IsAuthenticated,)
    
    class LandCreateInputSerializer(serializers.Serializer):
        background=serializers.CharField(required=False,default=1)
        user_id=serializers.CharField(required=False)
    class UserLandItemListInputSerializer(serializers.Serializer):
        email = serializers.CharField()
        
    class ItemImageSerializer(serializers.Serializer):
        image = serializers.ImageField()

    class LocationSerializer(serializers.Serializer):
        x = serializers.FloatField()
        y = serializers.FloatField()
        z = serializers.FloatField()
        show = serializers.BooleanField()

    class ItemSerializer(serializers.Serializer):
        no = serializers.IntegerField()
        item_image = serializers.SerializerMethodField()
        locations = serializers.SerializerMethodField()

        def get_item_image(self, obj):
            return obj.item_image.image if obj.item_image else None

        def get_locations(self, obj):
            user_email = self.context.get('user_email')
            try:
                location, created = obj.locations.get_or_create(
                    land__user__email=user_email,
                    defaults={
                        'x': 0,
                        'y': 0,
                        'z': 0,
                        'show': False
                    }
                )
            except Exception as e:
                # 예외가 발생하면 적절한 에러 메시지를 반환합니다.
                return {'error': str(e)}
                    
            return LandApi.LocationSerializer(location).data
    
    class LandItemOutputSerializer(serializers.Serializer):
        land = serializers.SerializerMethodField()
        items = serializers.SerializerMethodField()

        def get_land(self, obj):
            print(obj)
            print(f"Object type: {type(obj)}")
            s3_base_url = "https://s3.ap-northeast-2.amazonaws.com/cognisle.shop/media/lands/background/"
            land_img = f'{s3_base_url}land{obj.background}.png'
            bg_img = f'{s3_base_url}bg{obj.background}.png'
            return {'state': int(obj.background), 'land_img': land_img, 'bg_img': bg_img}

        def get_items(self, obj):
            request = self.context.get('request')
            items = self.context.get('items')

            if obj.user == request.user:
                # 소유자면 모든 아이템 반환
                return LandApi.ItemSerializer(items, many=True,context={'user_email':self.context.get('user_email')}).data
            else:
                # 사용된 아이템만 필터링하여 반환
                used_items = []
                for item in items:
                    if item.locations.filter(land=obj, show=True).exists():
                        used_items.append(item)
                return LandApi.ItemSerializer(used_items, many=True,context={'user_email':self.context.get('user_email')}).data
            
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
    @swagger_auto_schema(
        query_serializer=UserLandItemListInputSerializer,
        operation_id='섬 꾸미기 상태 조회 API',
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
    ## 쿼리 파라미터로 변경 & 유저 아이디 대신 유저 이메일로 조회        
    def get(self, request):
        email_serializer=self.UserLandItemListInputSerializer(data=request.query_params)
        email_serializer.is_valid(raise_exception=True)
        user_email=email_serializer.validated_data.get('email')
        user=get_object_or_404(User,email=user_email)
        land=LandSelector.get_user_land(user_email=user_email)
        items=LandSelector.get_user_items(user_email=user_email)
        logger.info(f"Lands and items retrieved: {land}")
        output_serializer = self.LandItemOutputSerializer(land, context={'user_email':user_email,'request': request,'items':items})
        # if request.user.id == user_id:
        #     output_serializer = self.LandItemOutputSerializer(lands_items, many=True)
        # else:
        #     output_serializer = self.PublicLandItemOutputSerializer(lands_items, many=True)
        return Response(
            {'status':'sucess',
             'data':{'owner':{'email':user.email,
                              'name':user.name},
                     'land':output_serializer.data.get('land'),
                     'items':output_serializer.data.get('items')}}, status=status.HTTP_200_OK)

class ItemImageCreateApi(APIView):
    permission_classes=(IsAuthenticated,)
    
    class ItemImageCreateInputSerializer(serializers.Serializer):
        image=serializers.ImageField()
        name=serializers.CharField(required=False)
    
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
            name=data.get('name'),
        )
        
        return Response({
            'status':'success',
            'data':{'img_pk':image_pk,
                'url':item_img_url},
        },status=status.HTTP_201_CREATED)
        
class ItemSerializer(serializers.Serializer):
    no=serializers.IntegerField()
    own=serializers.BooleanField()
    
class ItemCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class ItemCreateInputSerializer(serializers.Serializer):
        image_id = serializers.CharField()
        no=serializers.IntegerField()
    class LocationUpdateInputSerializer(serializers.Serializer):
        no = serializers.IntegerField()
        x = serializers.IntegerField()
        y = serializers.IntegerField()
        z = serializers.IntegerField()
        show = serializers.BooleanField()
        
    class MultipleLocationUpdateSerializer(serializers.Serializer):
        items = serializers.ListField(child=serializers.DictField(),required=False)
        land_back_id = serializers.IntegerField(required=False, allow_null=True)
    
    class ItemListIntputSerializer(serializers.Serializer):
        email=serializers.CharField()
        
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
            no=data.get('no'),
            # user=request.user,
        )
        
        print(item.item_image)
        return Response({
            'status':'success',
            'data':{
                'item_pk':item.pk,
                'item_image':item.item_image.image,
                'item_no':item.no,
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
        locations_data = data.get('items',[])
        print(locations_data)
        print(f"Land back ID: {land_back_id}")
        for location_data in locations_data:
            item = get_object_or_404(Item, no=location_data['no'])
            user_emails = item.users.values_list('email', flat=True)
            if request.user.email not in user_emails:
                raise PermissionDenied(f"You do not have permission to update the location of item {item.no}.")

            # 기존 위치 정보를 가져오거나 생성합니다.
            location, created = Location.objects.get_or_create(item=item,land=request.user.lands)

            location.x = str(location_data['x'])
            location.y = str(location_data['y'])
            location.z = str(location_data['z'])
            #show 여부 저장
            location.show=location_data['show']
            location.save()

            
        if land_back_id:
            land = get_object_or_404(Land,user=request.user)
            print('here')
            if request.user !=land.user:
                raise PermissionDenied(f"You do not have permission to update the land of {land.user}.")
            land.background=land_back_id 
            land.save()
            
        return Response({
            'status': 'success',
            'data': {
                'updated_items': [{
                    'no': location_data['no'],
                    'locations': {
                        'x': location_data['x'],
                        'y': location_data['y'],
                        'z': location_data['z'],
                        'show':location_data['show'],
                    }
                } for location_data in locations_data],
                'land_background_id':land_back_id,
            }
        }, status=status.HTTP_200_OK)    
    
    @swagger_auto_schema(
        query_serializer=ItemListIntputSerializer,
        operation_id='유저가 소유한 아이템 조회 API',
        operation_description="특정 유저가 어떤 아이템을 소유하고 있는지 아이템 no를 기준으로 조회하는 api",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                        "data":[
                            {
                                "no": 1,
                                "own": 'true'
                            },
                            {
                                "no": 2,
                                "own": 'true'
                            },
                            {
                                "no": 3,
                                "own": 'true'
                            },
                           {
                               "no": 4,
                                "own": 'false'
                            },
                            {
                                "no": 5,
                                "own": 'false'
                            }
                        ]
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )
    
    def get(self,request):
        email_serializer=self.ItemListIntputSerializer(data=request.query_params)
        email_serializer.is_valid(raise_exception=True)
        email=email_serializer.validated_data.get('email')

        items_nos=LandSelector.get_user_items_no(user_email=email)
        all_items_nos=range(1,25)
        
        result=[
            {'no':no,"own":no in items_nos}
            for no in all_items_nos
        ]
        
        return Response({
            'status':'success',
            'data':result
        },status=status.HTTP_200_OK)    
#아이템 show 변경 api(사용->사용X시)
class ItemShowUpdateApi(APIView):
    permission_classes=(IsAuthenticated,)
    class ItemShowUpdateSerializer(serializers.Serializer):
        item_nos = serializers.ListField(child=serializers.IntegerField())
        
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
    def put(self, request, *args, **kwargs):
        serializer = self.ItemShowUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        item_nos=data.get('item_nos')
        result=[]
        for item_no in item_nos:
            item = get_object_or_404(Item, no=item_no)
            # 현재 로그인한 유저가 해당 아이템의 소유자인지 확인
            user_emails = item.users.values_list('email', flat=True)
            if request.user.email not in user_emails:
                raise PermissionDenied("You do not have permission to update this item.")
            
            result.append({"item_no":item.no, "state":ItemService.show_or_no(item=item,user=request.user)})
        
        return Response({
            'status':'success',
            'data':{'show':result},
        },status=status.HTTP_200_OK)


class ItemGetApi(APIView):
    permission_classes=(IsAuthenticated,)
    
    class ItemGetInputSerializer(serializers.Serializer):
        item_nos = serializers.ListField(child=serializers.IntegerField())
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
        
        item_nos = data.get('item_nos')
        new_item_nos=[]
        
        for item_no in item_nos:
            item = get_object_or_404(Item,no=item_no)
            user_emails = item.users.values_list('email', flat=True)
            if request.user.email not in user_emails:
                item.users.add(request.user)
                item.save()  # 변경 사항 저장
                Location.objects.create(
                    item=item,
                    land=request.user.lands,
                    x=0,y=0,z=0,
                )
                new_item_nos.append(item_no)
        return Response({'status': 'success',
                         'new_item_ids':new_item_nos}, status=200)   
