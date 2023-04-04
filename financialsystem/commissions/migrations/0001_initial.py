# Generated by Django 4.1.5 on 2023-04-04 18:18

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('adviser', '0001_initial'),
        ('cashregister', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest_credit', models.DecimalField(decimal_places=2, default=40, help_text='Interes general para creditos', max_digits=5)),
                ('interest_register', models.DecimalField(decimal_places=2, default=7.5, help_text='Comision por registro', max_digits=5)),
                ('interest_payment', models.DecimalField(decimal_places=2, default=5, help_text='Comision por cobro', max_digits=5)),
                ('interest_sell', models.DecimalField(decimal_places=2, default=2, help_text='Comision por venta', max_digits=5)),
                ('points_score_refinancing', models.DecimalField(blank=True, decimal_places=2, default=80, help_text='Puntos por refinanciacion pagada', max_digits=5, null=True)),
                ('points_score_credits', models.DecimalField(blank=True, decimal_places=2, default=100, help_text='Puntos por credito pagado', max_digits=5, null=True)),
                ('daily_interest', models.DecimalField(blank=True, decimal_places=2, default=5, help_text='Disminucion de puntos por retraso diario', max_digits=5, null=True)),
                ('porcentage_daily_interest', models.DecimalField(blank=True, decimal_places=2, default=2, help_text='Porcentaje de interes por retraso diario', max_digits=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Commission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_paid', models.BooleanField(default=False)),
                ('interest', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('operation_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('type', models.CharField(choices=[('REGISTRO', 'REGISTRO'), ('COBRO', 'COBRO'), ('VENTA', 'VENTA')], max_length=20, null=True)),
                ('money_type', models.CharField(choices=[('PESOS', 'PESOS'), ('USD', 'USD'), ('EUR', 'EUR'), ('TRANSFER', 'TRANSFERENCIA')], default='PESOS', max_length=20, null=True)),
                ('last_up', models.DateTimeField(default=datetime.datetime.now)),
                ('detail', models.TextField(blank=True, help_text='Detalle de la operacion', max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('adviser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adviser.adviser')),
                ('mov', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cashregister.movement')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
