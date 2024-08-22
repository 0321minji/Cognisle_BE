from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from users.models import User

# Create your views here.
class FriendApi(APIView):
    permission_classes = (IsAuthenticated,)
    
    class FindFriendInputSerializer(serializers.Serializer):
        email=serializers.EmailField()
        
    class FindFriendOutputSerializer(serializers.Serializer):
        name=serializers.CharField()
        email=serializers.EmailField()
    
    def get(self,request):
        serializers=self.FindFriendInputSerializer(data=request.query_params)
        serializers.is_valid(raise_exception=True)
        email=serializers.validated_data.get('email')
        user=get_object_or_404(User,email=email)
        
        if user==request.user:
            print('here')
            return Response({
                'status':'fail',
                'data':"자기 자신을 검색할 수 없습니다.",
            })
        
        user_data = {
            'name': user.name,
            'email': user.email,
            }
        
        output_serializer=self.FindFriendOutputSerializer(data=user_data)
        output_serializer.is_valid(raise_exception=True)
        
        return Response({
            'status':'success',
            'data':output_serializer.data,
        })