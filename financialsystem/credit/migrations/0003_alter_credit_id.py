# Generated by Django 4.1.2 on 2023-02-26 22:28

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0002_alter_credit_mov_alter_refinancing_mov'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credit',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]