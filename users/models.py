from django.db import models

from core.models import TimeStampedModel
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password, name, **extra_fields):
        if not email:
            raise ValueError(('THe Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email,  name=name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email,  password, discord_id, nickname,  **extra_fields):
        #Django BaseUserManager의 기본 
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(('Superuser must have is_superuser=True.'))
        return self.create_user(email, password,discord_id, nickname,  **extra_fields)

class User(AbstractBaseUser,PermissionsMixin,TimeStampedModel):
    email = models.EmailField(max_length=64,unique=True)
    dsId = models.CharField(max_length=64,unique=True)
    name = models.CharField(max_length=20)
    dsName=models.CharField(max_length=20,null=True)
    is_active = models.BooleanField(default = True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['dsId', 'name']
    objects = UserManager()

    def __str__(self):
        return self.email