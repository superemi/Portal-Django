# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-26 13:55
from __future__ import unicode_literals

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20160521_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='headimg',
            field=models.ImageField(blank=True, default='', upload_to=main.models.User.headimg_upload_to),
        ),
    ]