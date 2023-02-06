# Generated by Django 4.1.5 on 2023-02-06 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cashregister", "0002_movement_created_at_movement_updated_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="movement",
            name="money_type",
            field=models.CharField(
                choices=[
                    ("PESO", "PESO"),
                    ("USD", "USD"),
                    ("EUR", "EUR"),
                    ("TRANSFER", "TRANSFER"),
                    ("CREDITO", "CREDITO"),
                    ("DEBITO", "DEBITO"),
                ],
                help_text="money type",
                max_length=20,
            ),
        ),
    ]
