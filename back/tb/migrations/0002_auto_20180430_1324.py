# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-04-30 05:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tb', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment_iscomplained',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user_blog',
            name='user_blog_focus',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user_blog',
            name='user_blog_like',
            field=models.NullBooleanField(default=False),
        ),
    ]
