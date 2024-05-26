from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.Land)
class Land(admin.ModelAdmin):
    pass

@admin.register(models.Item)
class Item(admin.ModelAdmin):
    pass

@admin.register(models.Location)
class Location(admin.ModelAdmin):
    pass