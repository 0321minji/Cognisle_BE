from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .services import FriendService
from users.models import User

# Create your views here.
class FriendApi(APIView):
    permission_classes = (IsAuthenticated,)
    
    class FindFriendInputSerializer(serializers.Serializer):
        email=serializers.EmailField()
        
    class FindFriendOutputSerializer(serializers.Serializer):
        name=serializers.CharField()
        email=serializers.EmailField()
    
    #친구 검색하기
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
    
    #친구 신청 보내기
    def post(self,request):
        input_serializer = self.FindFriendInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data=input_serializer.validated_data
        
        email=data.get('email')
        to_friend=get_object_or_404(User,email=email)
        if to_friend==request.user:
            return Response({
                "status":'fail',
                "data":"자기 자신에게 친구 신청을 보낼 수 없습니다."
            })
        
        service=FriendService()
        
        res=service.send(
            to=to_friend,
            fr=request.user,
        )
        
        if res=='case1':
            return Response({
                "status":'error1',
                'data':'이미 친구 상태입니다.'
            })
        elif res=='case2':
            return Response({
                'status':'error2',
                "data":'이미 친구 신청을 보낸 상태입니다.'
            })
        elif res=='case3':
            return Response({
                "status":"error3",
                "data":'상대가 친구 신청을 보낸 상태입니다.'
            })
        return Response({
            "status":"success",
            "data":{"name":to_friend.name,
                    "email":to_friend.email}
        })
        
        
        