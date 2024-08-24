from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .services import FriendService
from users.models import User
from friends.models import Friend, FriendRequest

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
        serializers.is_valid()
        email=serializers.validated_data.get('email')
        if email:
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
            },status=status.HTTP_200_OK)
        else:
            friend, created = Friend.objects.get_or_create(user=request.user)
            serializer = self.FindFriendOutputSerializer(friend.friends.all(), many=True)
            return Response({
                "status": "success",
                "data": serializer.data
            },status=status.HTTP_200_OK)
    
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
        },status=status.HTTP_200_OK)
        
class AcceptRequestApi(APIView):
    permission_classes=(IsAuthenticated,)
    
    class AcceptRequestInputSerializer(serializers.Serializer):
        email=serializers.EmailField()
    
    def post(self,request):
        serializers=self.AcceptRequestInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        email=serializers.validated_data.get('email')
        from_user=get_object_or_404(User,email=email)
        friend_request=FriendRequest.objects.filter(from_user=from_user,to_user=request.user).first()

        if not friend_request:
            return Response({
                "status": "fail",
                "message": "해당 요청이 존재하지 않습니다."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            friend_request.accept()
        except Exception as e:
            return Response({
                "status": "fail",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            "data": {
                "from_user": {
                    "name": from_user.name,
                    "email": from_user.email
                },
                "to_user": {
                    "name": request.user.name,
                    "email": request.user.email
                }
            }
        }, status=status.HTTP_200_OK)
        
class RejectRequestApi(APIView):
    permission_classes=(IsAuthenticated,)
    
    class RejectRequestInputSerializer(serializers.Serializer):
        email=serializers.EmailField()
    
    def post(self,request):
        serializers=self.RejectRequestInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        email=serializers.validated_data.get('email')
        from_user=get_object_or_404(User,email=email)
        friend_request=FriendRequest.objects.filter(from_user=from_user,to_user=request.user).first()
        
        if not friend_request:
            return Response({
                "status": "fail",
                "message": "해당 요청이 존재하지 않습니다."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            friend_request.reject()
        except Exception as e:
            return Response({
                "status": "fail",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            # "data": {
            #     "from_user": {
            #         "name": from_user.name,
            #         "email": from_user.email
            #     },
            #     "to_user": {
            #         "name": request.user.name,
            #         "email": request.user.email
            #     }
            # }
        }, status=status.HTTP_200_OK)

class RequestApi(APIView):
    permission_classes=(IsAuthenticated,)

    class RequestOutputSerializer(serializers.Serializer):
        name=serializers.CharField(source='from_user.name')
        email=serializers.EmailField(source='from_user.email')
        
    def get(self,request):
        user=request.user
        
        friend_requests=FriendRequest.objects.filter(to_user=user)
        print(friend_requests)
        serializer=self.RequestOutputSerializer(friend_requests,many=True)
        
        return Response({
            "status":'success',
            "data":serializer.data,
        },status=status.HTTP_200_OK)