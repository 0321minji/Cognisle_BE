from django.shortcuts import render
from django.shortcuts import get_object_or_404
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
# Create your views here.
class LandCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class LandCreateInputSerializer(serializers.Serializer):
        background=serializers.CharField(required=False)
        items=serializers.ListField(required=False)
        
    def post(self,request):
        serializers=self.LandCreateInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data=serializers.validated_data
        
        service=LandCoordinatorService(user=request.user)
        
        land=service.create(
            background=data.get('background'),
            items=data.get('items',[]),
        )
        
        if land:
            return Response({
                'status' : 'success',
                'data' : {'id': land.id},
            },status=status.HTTP_201_CREATED)
            
class ItemImageCreateApi(APIView):
    permission_classes=(IsAuthenticated,)
    
    class ItemImageCreateInputSerializer(serializers.Serializer):
        image=serializers.ImageField()
    
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

    
    def post(self,request):
        serializer=self.ItemCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=serializer.validated_data
        
        item=ItemService.create(
            image_id=data.get('image_id'),
            show=False,
            user=request.user,
        )
        
        return Response({
            'status':'success',
            'data':{
                'item_pk':item.pk,
                'item_image':item.item_image.image.url,
                'item_show':item.show,
            }
        })

#아이템 show 변경 api(사용->사용X시)
class ItemShowUpdateApi(APIView):
    permission_classes=(IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        item_id=request.data.get('item_id')
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
        show = serializers.BooleanField()
        item_image = serializers.SerializerMethodField()
        locations = serializers.SerializerMethodField()

        def get_item_image(self, obj):
            return obj.item_image.image.url if obj.item_image else None

        def get_locations(self, obj):
            if obj.show:
                return UserLandItemListApi.LocationSerializer(obj.locations.all(), many=True).data
            return []

    class LandItemOutputSerializer(serializers.Serializer):
        lands = serializers.SerializerMethodField()
        items = serializers.SerializerMethodField()

        def get_lands(self,obj):
            s3_base_url="https://s3.amazonaws.com/cognisle.shop/media/lands/background/"
            land_img=f'{s3_base_url}land{obj.background}'
            bg_img=f'{s3_base_url}bg{obj.background}'
            return {'state':obj.background,'land_img': land_img, 'bg_img': bg_img}
        
        def get_items(self, obj):
            return UserLandItemListApi.ItemSerializer(obj.lands.all(), many=True).data
        
    class PublicLandItemOutputSerializer(serializers.Serializer):
        lands = serializers.SerializerMethodField()
        items = serializers.SerializerMethodField()

        def get_lands(self, obj):
            s3_base_url = "https://s3.amazonaws.com/cognisle.shop/media/lands/background/"
            land_img = f'{s3_base_url}land{obj.background}'
            bg_img = f'{s3_base_url}bg{obj.background}'
            return {'state': obj.background, 'land_img': land_img, 'bg_img': bg_img}

        def get_items(self, obj):
            return UserLandItemListApi.ItemSerializer(obj.lands.filter(show=True), many=True).data
        
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        print(user.email)
        print(request.user.id)
        logger.info(f"Fetching lands and items for user_id: {user_id}")

        lands_items = LandSelector.get_lands_and_items(user_id=user_id)
        logger.info(f"Lands and items retrieved: {lands_items}")
        lands_items = LandSelector.get_lands_and_items(user_id=user_id)
        if request.user.id == user_id:
            output_serializer = self.LandItemOutputSerializer(lands_items, many=True)
        else:
            output_serializer = self.PublicLandItemOutputSerializer(lands_items, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

class ItemLocationUpdateApi(APIView):
    permission_classes = (IsAuthenticated,)
    class LocationUpdateInputSerializer(serializers.Serializer):
        item_id = serializers.IntegerField()
        x = serializers.CharField(max_length=100)
        y = serializers.CharField(max_length=100)
        z = serializers.CharField(max_length=100)

    class MultipleLocationUpdateSerializer(serializers.Serializer):
        locations = serializers.ListField(child=serializers.DictField())

    @transaction.atomic
    def post(self, request):
        serializer = self.MultipleLocationUpdateSerializer(data=request.data)
        if serializer.is_valid():
            locations_data = serializer.validated_data['locations']

            for location_data in locations_data:
                item = get_object_or_404(Item, pk=location_data['item_id'])

                if request.user != item.user:
                    raise PermissionDenied(f"You do not have permission to update the location of item {item.id}.")

                # 기존 위치 정보를 가져오거나 생성합니다.
                location, created = Location.objects.get_or_create(item=item)
                
                # 위치 정보를 업데이트합니다.
                location.x = location_data['x']
                location.y = location_data['y']
                location.z = location_data['z']
                location.save()
                
                if created:
                    item.show=True
                    item.save()

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
                    } for location_data in locations_data]
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)