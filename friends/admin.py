from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Friend)
class Friend(admin.ModelAdmin):
    pass

@admin.register(models.FriendRequest)
class FriendRequest(admin.ModelAdmin):
    pass