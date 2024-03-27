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
        #phone=serializers.CharField()
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
            phone=request.session['verify_phone'],
        )
        
        return Response({
            'status':'success',
        },status=status.HTTP_201_CREATED)

class SendAPI(APIView):
    permission_classes=(AllowAny,)
    
    class SendInputSerializer(serializers.Serializer):
        phone=serializers.CharField()
        
    def post(self,request):
        serializers = self.SendInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data=serializers.validated_data
                 
        auth_num=UserService.user_phone_verify(
            to_phone=data.get('phone')
        )
        request.session['auth_num']=auth_num
        request.session['phone']=data.get('phone')
    
        return Response({
            'status':'send success',
        },status=status.HTTP_200_OK)        

       
class VerifyAPI(APIView):
    permission_classes=(AllowAny,)
    
    class VerifyInputSerializer(serializers.Serializer):
        auth_num=serializers.IntegerField()
        
    def post(self,request):
        serializers = self.VerifyInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data=serializers.validated_data
        
        stored_auth_num=request.session.get('auth_num')
        
        auth_num=data.get('auth_num')
        print(stored_auth_num,auth_num)
        
        if stored_auth_num==auth_num:
            request.session['verify_phone']=request.session['phone']
            del request.session['auth_num']
            return Response({
                'status':'verify success'
            },status=status.HTTP_200_OK)
        else:
            request.session.flush()
            return Response({
                'status':'verify fail'
            },status=status.HTTP_400_BAD_REQUEST)
        
        