# Generated by Django 4.1.5 on 2023-04-01 04:22

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('adviser', '0001_initial'),
        ('credit', '0001_initial'),
        ('cashregister', '0001_initial'),
        ('commissions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Warranty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_selled', models.BooleanField(default=False)),
                ('article', models.CharField(help_text='Articulo', max_length=50, verbose_name='Articulo')),
                ('purchase_papers', models.BooleanField(blank=True, default=False, help_text='Papeles de compra', verbose_name='Papeles de compra')),
                ('brand', models.CharField(help_text='Marca', max_length=50, verbose_name='Marca')),
                ('model', models.CharField(help_text='Modelo', max_length=50, verbose_name='Modelo')),
                ('accessories', models.CharField(help_text='Accesorios', max_length=50, verbose_name='Accesorios')),
                ('state', models.CharField(blank=True, choices=[('NUEVO', 'NUEVO'), ('USADO:COMO NUEVO', 'USADO:COMO NUEVO'), ('USADO:MUY BUENO', 'USADO:MUY BUENO'), ('USADO:BUENO', 'USADO:BUENO'), ('USADO:ACEPTABLE', 'USADO:ACEPTABLE'), ('USADO:REACONDICIONADO', 'USADO:REACONDICIONADO'), ('USADO:MUCHO USO', 'USADO:MUCHO USO')], max_length=30, verbose_name='Estado')),
                ('detail', models.TextField(blank=True, help_text='Observaciones del articulo', max_length=150, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('credit', models.ForeignKey(blank=True, default=None, help_text='Empeño del usuario', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='warranty_client', to='credit.credit')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Sell',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('payment_method', models.CharField(blank=True, choices=[('PESOS', 'PESOS'), ('USD', 'USD'), ('EUR', 'EUR'), ('TRANSFER', 'TRANSFERENCIA'), ('DEBITO', 'DEBITO'), ('CREDITO', 'CREDITO')], default='PESOS', max_length=15, null=True)),
                ('sell_date', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('detail', models.TextField(blank=True, help_text='Observaciones del articulo', max_length=150, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('adviser', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adviser.adviser')),
                ('article', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sell', to='warranty.warranty')),
                ('commission', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='commissions.commission')),
                ('mov', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cashregister.movement')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
