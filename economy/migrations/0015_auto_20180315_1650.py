# Generated by Django 2.0.3 on 2018-03-15 20:50

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('economy', '0014_auto_20180314_1326'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='staff_only',
        ),
        migrations.AddField(
            model_name='room',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
