# Generated by Django 4.1.7 on 2023-03-08 21:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warranty', '0005_sell_commission'),
    ]

    operations = [
        migrations.AddField(
            model_name='sell',
            name='sell_date',
            field=models.DateTimeField(default=datetime.datetime.now, null=True),
        ),
    ]