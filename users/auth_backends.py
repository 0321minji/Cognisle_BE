# users/auth_backends.py

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
import bcrypt

User = get_user_model()

class BcryptSuperuserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
            # 비밀번호가 맞는지 bcrypt로 검증
            print(password,user.password)
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
