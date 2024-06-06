from users.models import User
from lands.models import Item, Land, Location
from django.db.models import Q, F, Value, CharField, Case, When, Exists, OuterRef
from django.db.models.functions import Concat, Substr
import re
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
@dataclass
class ItemDto:
    id: int
    show: bool
    user: dict
    location : Optional[List[dict]] =None

class ItemSelector:
    def __init__(self):
        pass
    
    @staticmethod
    def list(filter: bool, user:User):
        q=Q()
        if filter:
            q.add(Q(show=filter),q.AND)
        if user:
            q.add(Q(user=user),q.AND)
            
        items = Item.objects.filter(q).prefetch_related('locations')
        item_dtos=[ItemDto(
            id=item.id,
            show=item.show,
            location=[{
                        'x': loc.x,
                        'y': loc.y,
                        'z': loc.z,
                    } for loc in item.locations.all()],
            user={
                'nickname':user.nickname,
                'email':user.email,
            }
        ) for item in items]
        return item_dtos