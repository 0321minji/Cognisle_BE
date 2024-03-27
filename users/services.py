from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
# from django.utils.encoding import force_str, force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.template.loader import render_to_string
from datetime import timedelta
import environ, os
from pathlib import Path
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from twilio.rest import Client
import random
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
from users.models import User
# from core.exceptions import ApplicationError

class UserService:
    def __init__(self):
        pass
    
    def user_sign_up(email:str,password:str, discord_id:str, nickname:str,phone:str):

        user=User(email=email, password=password, discord_id=discord_id,nickname=nickname,phone=phone)
        
        user.set_password(password)
        user.is_active=False
        user.save()
    
    def user_phone_verify(to_phone:str):
        account_sid=env('ACCOUNT_SID')
        auth_token=env('AUTH_TOKEN')
        auth_number=random.randint(1000, 10000)
        client = Client(account_sid,auth_token)
        from_phone='+16562212841'
        content='인증 번호 [{}]를 입력해주세요.'.format(auth_number)
        message = client.messages.create(to=to_phone,from_=from_phone,body=content)    
        return auth_number
