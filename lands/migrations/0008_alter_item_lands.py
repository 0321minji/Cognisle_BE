# Generated by Django 4.0 on 2024-07-16 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lands', '0007_rename_land_item_lands_rename_user_item_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='lands',
            field=models.ManyToManyField(related_name='items', to='lands.Land'),
        ),
    ]
