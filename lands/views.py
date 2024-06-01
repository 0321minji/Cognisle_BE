from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers, status
from rest_framework.response import Response

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