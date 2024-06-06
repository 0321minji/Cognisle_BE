from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers, status
from rest_framework.response import Response
from .selectors import ItemSelector
from .models import Land, Location, Item, ItemImage
from .services import LandCoordinatorService, ItemImageService
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
        
        item_img_url=ItemImageService.create(
            image=data.get('image'),
        )
        
        return Response({
            'status':'success',
            'data':{'url':item_img_url},
        },status=status.HTTP_201_CREATED)
        
#전체 아이템 리스트(모든 소유 아이템)
class ItemListApi(APIView):
    permission_classes=(IsAuthenticated,)
    
    class ItemListFilterSerializer(serializers.Serializer):
        #filter 소유한 아이템 중 사용/미사용 , 필터 사용 X시 소유한 모든 아이템
        filter=serializers.BooleanField(required=False)
        
    class ItemListOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        show = serializers.BooleanField()
        location = serializers.ListField(child=serializers.DictField())
        
    def get(self, request):
        filters_serializer=self.ItemListFilterSerializer(
            data=request.query_params
        )
        filters_serializer.is_valid(raise_exception=True)
        filters = filters_serializer.validated_data
        
        items=ItemSelector.list(
            filter=filters.get('filter',''),
            user=request.user,
        )
        output=self.ItemListOutputSerializer(items,many=True)
        return Response(output.data,status=status.HTTP_200_OK)