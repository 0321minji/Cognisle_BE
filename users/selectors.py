from django.http import Http404, HttpResponseBadRequest
from users.models import User
import bcrypt

class UserSelector:
    def __init__(self):
        pass
    
    @staticmethod
    def get_user_by_email(email:str)->User:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise Http404
        except User.MultipleObjectsReturned:
            raise Http404
    
    @staticmethod
    def check_password(user:User, password:str):
        # return user.check_password(password)
        password=password.encode('utf-8')
        print(password,user.password)
        return bcrypt.checkpw(password,user.password.encode('utf-8'))