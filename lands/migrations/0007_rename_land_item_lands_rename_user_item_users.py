# Generated by Django 4.0 on 2024-07-16 13:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lands', '0006_remove_item_land_item_land_remove_item_user_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='land',
            new_name='lands',
        ),
        migrations.RenameField(
            model_name='item',
            old_name='user',
            new_name='users',
        ),
    ]