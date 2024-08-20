from django.shortcuts import render
from users.models import User
from lands.models import Land, Item
# Create your views here.
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.services import UserService
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import requests, threading
from django.shortcuts import get_object_or_404

def post_request_in_background(url, headers):
    try:
        response = requests.post(url, headers=headers)
        print("Background request complete:", response.status_code)
    except Exception as e:
        print("Background request failed:", str(e))
        
class UserSignUpApi(APIView):
    permission_classes=(AllowAny,)
    
    class UserSignUpInputSerializer(serializers.Serializer):
        email=serializers.EmailField()
        password=serializers.CharField()
        dsId=serializers.CharField(required=False)
        dsName=serializers.CharField(required=False)
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
        print(signup_data)
        print(signup_data.get('email'))
        return Response({
            'status':'success',
            'data':{'email':signup_data.get('email'),
                    'name':signup_data.get('name'),
                    'dsId':signup_data.get('dsId')}
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
        dsName=serializers.CharField(required=False,allow_blank=True)
        dsId=serializers.CharField(required=False,allow_null=True,allow_blank=True)
        user_id=serializers.CharField()
        
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
        
        user = get_object_or_404(User, email=data.get('email'))
        land, created = Land.objects.get_or_create(user=user)
        
        response={
            'status': 'success',
            'data': output_serializer.data,
        }
        if created:
            response['land']=f'A new land has been created for {user.name}'
        return Response(response, status=status.HTTP_200_OK)
    
# class UserListApi(APIView):
#     permission_classes=(AllowAny,)
    
#     def get(self,request):
#         user_lists= UserSelector   
# 일단 특정 유저에 대한 detail api 

class UserDetailApi(APIView):
    permission_classes=(IsAuthenticated,)
    class LandSerializer(serializers.ModelSerializer):
        pk = serializers.IntegerField()
        class Meta:
            model = Land
            fields = ['pk']
            
    class ItemSerializer(serializers.Serializer):
        pk = serializers.IntegerField()
        show = serializers.BooleanField()
        
    class UserDetailOuputSerializer(serializers.Serializer):
        pk = serializers.IntegerField()
        email = serializers.EmailField()
        dsId = serializers.CharField()
        name = serializers.CharField()
        dsName = serializers.CharField()
        is_active = serializers.BooleanField()
        is_staff = serializers.BooleanField()
        land_id = serializers.SerializerMethodField()
        items_id_list = serializers.SerializerMethodField()

        def get_land_id(self, obj):
            land = Land.objects.get(user=obj)
            return land.pk
        def get_items_id_list(self, obj):
            items = Item.objects.filter(users=obj)
            return [{'id': item.pk, 'show': item.show} for item in items]
    
    def get(self, request, user_pk):
        print(user_pk)
        
        user=get_object_or_404(User,pk=user_pk)
        print(user.email)
        serializers = self.UserDetailOuputSerializer(user)
        
        return Response({
            'status':'success',
            'data':serializers.data,
        },status=status.HTTP_200_OK)
    