# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-05-01 04:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tb', '0004_auto_20180501_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_blog',
            name='user_blog_createdat',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]