# Generated by Django 4.0 on 2024-05-26 10:25

from django.db import migrations, models
import django.db.models.deletion
import lands.models


class Migration(migrations.Migration):

    dependencies = [
        ('lands', '0004_rename_landlord_land_user_remove_land_items_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='item_image.png', upload_to=lands.models.get_item_pic_upload_path)),
            ],
        ),
        migrations.RemoveField(
            model_name='item',
            name='image',
        ),
        migrations.AddField(
            model_name='item',
            name='item_image',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='lands.itemimage'),
            preserve_default=False,
        ),
    ]
