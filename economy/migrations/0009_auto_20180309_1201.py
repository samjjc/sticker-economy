# Generated by Django 2.0.2 on 2018-03-09 17:01

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('economy', '0008_traderequest'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sticker',
            unique_together={('owner', 'title')},
        ),
    ]
