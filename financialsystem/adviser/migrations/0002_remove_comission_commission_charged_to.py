# Generated by Django 4.1.5 on 2023-02-27 14:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("adviser", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comission",
            name="commission_charged_to",
        ),
    ]
