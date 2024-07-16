from django.shortcuts import render
from users.models import User
# Create your views here.
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.services import UserService
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class UserSignUpApi(APIView):
    permission_classes=(AllowAny,)
    
    class UserSignUpInputSerializer(serializers.Serializer):
        email=serializers.EmailField()
        password=serializers.CharField()
        dsId=serializers.CharField()
        dsName=serializers.CharField()
        name=serializers.CharField()
        
    class UserSignUpOutputSerializer(serializers.Serializer):
        email=serializers.CharField()
        pk=serializers.CharField()
        dsId=serializers.CharField()
        dsName=serializers.CharField()
        name=serializers.CharField()
            
    @swagger_auto_schema(
        request_body=UserSignUpInputSerializer,
        security=[],
        operation_id='유저 회원가입 API',
        operation_description="유저 기본 회원가입 API 입니다.",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )    
    def post(self,request):
        serializers = self.UserSignUpInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data=serializers.validated_data
        
        signup_data=UserService.user_sign_up(
            email=data.get('email'),
            password=data.get('password'),
            dsId=data.get('dsId'),
            name=data.get('name'),
            dsName=data.get('dsName'),
        )
        
        output_serializer = self.UserSignUpOutputSerializer(data=signup_data)
        output_serializer.is_valid(raise_exception=True)
        
        return Response({
            'status':'success',
            'data':output_serializer.data,
        },status=status.HTTP_201_CREATED)

class UserLoginApi(APIView):
    permission_classes = (AllowAny,)
    
    class UserLoginInputSerializer(serializers.Serializer):
        email=serializers.CharField()
        password=serializers.CharField()
        
    class UserLoginOutputSerializer(serializers.Serializer):
        email=serializers.CharField()
        refresh=serializers.CharField()
        access=serializers.CharField()
        name=serializers.CharField()
        pk=serializers.CharField()
        
    @swagger_auto_schema(
        request_body=UserLoginInputSerializer,
        security=[],
        operation_id='유저 로그인 API',
        operation_description="유저 로그인 API 입니다.",
        responses={
            "200":openapi.Response(
                description="OK",
                examples={
                    "application/json":{
                        "status":"success",
                        'email':'test@naver.com',
                        'refresh':'refresh 토큰',
                        'access':'access 토큰',
                        'name':'test',
                    }
                }
            ),
            "400":openapi.Response(
                description="Bad Request",
            ),
        }
    )      
    
    def post(self,request):
        input_serializer = self.UserLoginInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data= input_serializer.validated_data
        
        service=UserService()
        
        login_data=service.login(
            email=data.get('email'),
            password=data.get('password'),
        )
        
        output_serializer = self.UserLoginOutputSerializer(data=login_data)
        output_serializer.is_valid(raise_exception=True)

        return Response({
            'status': 'success',
            'data': output_serializer.data,
        }, status = status.HTTP_200_OK)