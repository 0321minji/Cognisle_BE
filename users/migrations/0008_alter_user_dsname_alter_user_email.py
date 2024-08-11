# Generated by Django 4.0 on 2024-08-10 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_rename_discord_id_user_dsid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='dsName',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=64, null=True, unique=True),
        ),
    ]