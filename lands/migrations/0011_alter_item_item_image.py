# Generated by Django 4.0 on 2024-08-03 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lands', '0010_alter_land_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='item_image',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='lands.itemimage'),
        ),
    ]
