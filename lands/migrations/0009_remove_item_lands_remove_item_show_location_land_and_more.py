# Generated by Django 4.0 on 2024-08-01 14:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lands', '0008_alter_item_lands'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='lands',
        ),
        migrations.RemoveField(
            model_name='item',
            name='show',
        ),
        migrations.AddField(
            model_name='location',
            name='land',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='lands.land'),
        ),
        migrations.AddField(
            model_name='location',
            name='show',
            field=models.BooleanField(default=False),
        ),
    ]
