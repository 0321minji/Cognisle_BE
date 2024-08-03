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
import requests
from django.shortcuts import get_object_or_404

class UserSignUpApi(APIView):
    permission_classes=(AllowAny,)
    
    class UserSignUpInputSerializer(serializers.Serializer):
        email=serializers.EmailField()
        password=serializers.CharField()
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
        
        UserService.user_sign_up(
            email=data.get('email'),
            password=data.get('password'),
            dsId=data.get('dsId'),
            name=data.get('name'),
            dsName=data.get('dsName'),
        )
        
        return Response({
            'status':'success',
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
        dsName=serializers.CharField()
        dsId=serializers.CharField()
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

        landcreate_data = None
        try:
            land = Land.objects.get(user=user)
            landcreate_data=land.pk
        except Land.DoesNotExist:
            try:
                user_token = login_data.get('access')
                if user_token:
                    print(user_token)
                else:
                    return Response ({
                        'status':'error',
                    },status=status.HTTP_401_UNAUTHORIZED)
                headers = {
                    'Authorization': f'Bearer {user_token}'
                }
                print(headers)
                landcreate_response = requests.post('https://www.cognisle.shop/lands/create/', json={
                    'background': '1',
                    'items':[]
                }, headers=headers)
                print(landcreate_response.status_code, landcreate_response.content)
                landcreate_response.raise_for_status()
                landcreate_data = landcreate_response.json()
            except requests.exceptions.RequestException as e:
                return Response({
                    'status': 'error',
                    'message': 'User login successful, but failed to trigger landcreate.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'status': 'success',
            'data': output_serializer.data,
        }, status=status.HTTP_200_OK)
    
# class UserListApi(APIView):
#     permission_classes=(AllowAny,)
    
#     def get(self,request):
#         user_lists= UserSelector   
# 일단 특정 유저에 대한 detail api 
class UserDetailApi(APIView):
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
    