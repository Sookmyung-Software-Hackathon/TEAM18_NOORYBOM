# Generated by Django 4.0.6 on 2022-08-04 10:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20211107_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='followers',
            field=models.ManyToManyField(related_name='followings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='ranking',
            field=models.CharField(choices=[('1', 'Seed'), ('2', 'Sprout'), ('3', 'Seedling'), ('4', 'Tree'), ('5', 'Flower')], default='1', max_length=1),
        ),
        migrations.AddField(
            model_name='user',
            name='residence',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='user',
            name='sum_time',
            field=models.IntegerField(default=0),
        ),
    ]
