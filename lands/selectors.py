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
            
        items = Item.objects.filter(q).prefetch_related('locations', 'user')
        item_dtos = []
        for item in items:
            item_data = {
                'id': item.id,
                'show': item.show,
                'user': {
                    'nickname': item.user.nickname,
                    'email': item.user.email,
                }
            }
            if item.show:
                item_data['location'] = [{
                    'x': loc.x,
                    'y': loc.y,
                    'z': loc.z,
                } for loc in item.locations.all()]
            item_dtos.append(item_data)
        return item_dtos

    def show(self, item: Item):
        return item.show
    
class LandSelector:
    @staticmethod
    def get_lands_and_items(user_id):
        lands=Land.objects.filter(user_id=user_id).prefetch_related('lands__item_image','lands__locations')
        return lands