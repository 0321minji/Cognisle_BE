from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
# from django.utils.encoding import force_str, force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.template.loader import render_to_string
from datetime import timedelta
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from users.selectors import UserSelector
from users.models import User
import bcrypt
# from core.exceptions import ApplicationError

class UserService:
    def __init__(self):
        pass
    
    def user_sign_up(email:str,password:str, name:str,dsId:str=None, dsName:str=None):

        user=User(email=email, password=password, dsId=dsId,name=name,dsName=dsName)
        
        #user.set_password(password)
        user.password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.save()
        
        data={
            "email":user.email,
            'dsId':user.dsId,
            'name':user.name,
            'dsName':user.dsName,
            'pk':user.pk,
        }

        return data

    
    def login(self, email:str, password:str):
        selector = UserSelector()
        
        user = selector.get_user_by_email(email)
        
        if not selector.check_password(user,password):
            raise exceptions.ValidationError(
                {'datail':'아이디나 비밀번호가 올바르지 않습니다.'}
            )
        
        token = RefreshToken.for_user(user=user)
        
        data={
            "email":user.email,
            'refresh':str(token),
            'access':str(token.access_token),
            'name':user.name,
            'user_id':user.pk,
            'dsId':user.dsId or '' ,
            'dsName':user.dsName or '',
        }
        
        return data
        
