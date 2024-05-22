# Generated by Django 4.0 on 2024-05-19 14:26

from django.db import migrations, models
import django.db.models.deletion
import lands.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0006_alter_user_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.CharField(max_length=100)),
                ('y', models.CharField(max_length=100)),
                ('z', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Land',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('background', models.CharField(default=1, max_length=10)),
                ('landlord', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lands', to='users.user')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='item_pic.png', upload_to=lands.models.get_item_pic_upload_path)),
                ('show', models.BooleanField(default=False)),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lands', to='lands.location')),
            ],
        ),
    ]
