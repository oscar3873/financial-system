# Generated by Django 4.1.7 on 2023-03-09 15:00

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Adviser',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='adviser', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Comission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_paid', models.BooleanField(default=False)),
                ('interest', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('original_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('type', models.CharField(choices=[('REGISTRO', 'REGISTRO'), ('COBRO', 'COBRO'), ('VENTA', 'VENTA')], max_length=20, null=True)),
                ('money_type', models.CharField(choices=[('PESOS', 'PESOS'), ('USD', 'USD'), ('EUR', 'EUR'), ('TRANSFER', 'TRANSFERENCIA')], default=('PESOS', 'PESOS'), max_length=20, null=True)),
                ('last_up', models.DateTimeField(default=datetime.datetime.now)),
                ('detail', models.TextField(blank=True, help_text='Detalle de la operacion', max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('adviser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adviser.adviser')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
