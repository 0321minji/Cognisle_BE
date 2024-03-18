from django.shortcuts import render
from users.models import User
# Create your views here.
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.services import UserService

class UserSignUpApi(APIView):
    permission_classes=(AllowAny,)
    
    class UserSignUpInputSerializer(serializers.Serializer):
        email=serializers.EmailField()
        password=serializers.CharField()
        discord_id=serializers.CharField()
        phone=serializers.CharField()
        nickname=serializers.CharField()
        
    def post(self,request):
        serializers = self.UserSignUpInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data=serializers.validated_data
        
        UserService.user_sign_up(
            email=data.get('email'),
            password=data.get('password'),
            discord_id=data.get('discord_id'),
            nickname=data.get('nickname'),
            phone=data.get('phone'),
        )
        
        return Response({
            'status':'success',
        },status=status.HTTP_201_CREATED)