# Generated by Django 4.1.5 on 2023-02-13 05:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("note", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="note",
            name="user",
            field=models.ForeignKey(
                blank=True,
                default=None,
                help_text="Notas de Usuario",
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                related_name="user_notes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
