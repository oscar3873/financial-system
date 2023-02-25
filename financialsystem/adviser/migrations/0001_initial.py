# Generated by Django 4.1.7 on 2023-02-25 12:03

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cashregister', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checked', models.BooleanField(default=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('type', models.CharField(choices=[('REGISTRO', 'REGISTRO'), ('COBRO', 'COBRO')], default='Registro', max_length=20, null=True)),
                ('money_type', models.CharField(choices=[('PESOS', 'PESOS'), ('USD', 'USD'), ('EUR', 'EUR'), ('TRANSFER', 'TRANSFERENCIA')], default=('PESOS', 'PESOS'), max_length=20, null=True)),
                ('create_date', models.DateTimeField(default=datetime.datetime.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('adviser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('commission_charged_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='clients.client')),
                ('mov', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cashregister.movement')),
            ],
        ),
        migrations.CreateModel(
            name='Adviser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='adviser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
