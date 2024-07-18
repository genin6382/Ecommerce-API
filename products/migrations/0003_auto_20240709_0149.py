# Generated by Django 3.2.25 on 2024-07-08 20:19

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_productcategory_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productitem',
            name='product',
        ),
        migrations.AddField(
            model_name='productitem',
            name='category',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='products.productcategory'),
        ),
        migrations.AddField(
            model_name='productitem',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2024, 7, 9, 1, 49, 39, 582736)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productitem',
            name='description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='productitem',
            name='name',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='productitem',
            name='seller',
            field=models.CharField(default='', max_length=100),
        ),
    ]