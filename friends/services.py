from .models import Friend, FriendRequest
from .models import User
from django.shortcuts import get_list_or_404, get_object_or_404
from django.db import transaction
from django.utils import timezone

current_time = timezone.now()

class FriendService:
    def __init__(self):
        pass
    
    @staticmethod
    def send(to:User,fr:User):
        
        to_friend, create=Friend.objects.get_or_create(user=to)
        #from_friend=Friend.objects.get_or_create(email=fr.email)
        
        #이미 친구 상태
        is_friend = to_friend.friends.filter(id=fr.id).exists()
        if is_friend:
            return "case1"

        #이미 보낸 신청
        is_request = FriendRequest.objects.filter(from_user=fr,to_user=to).exists()
        if is_request:
            return "case2"
        
        # 이미 받은 신청
        is_response = FriendRequest.objects.filter(to_user=fr,from_user=to).exists()
        if is_response:
            return "case3"
            
        req=FriendRequest(
            to_user=to,
            from_user=fr,
            created_at=current_time
        )
        req.save()
        return req