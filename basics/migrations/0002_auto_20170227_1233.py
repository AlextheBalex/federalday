# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-27 12:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='name',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='party name'),
        ),
    ]
