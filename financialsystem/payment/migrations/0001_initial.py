# Generated by Django 4.1.5 on 2023-03-31 17:13

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('credit', '0001_initial'),
        ('commissions', '0001_initial'),
        ('adviser', '0001_initial'),
        ('cashregister', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, default=0, help_text='Monto de Pago', max_digits=15)),
                ('payment_date', models.DateTimeField(default=datetime.datetime.now, help_text='Fecha de Pago')),
                ('payment_method', models.CharField(choices=[('PESOS', 'PESOS'), ('USD', 'USD'), ('EUR', 'EUR'), ('TRANSFER', 'TRANSFER'), ('CREDITO', 'CREDITO'), ('DEBITO', 'DEBITO')], help_text='Metodo de Pago', max_length=20)),
                ('detail', models.CharField(blank=True, max_length=150, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('adviser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adviser.adviser')),
                ('commission_to', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='commissions.commission')),
                ('installment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='credit.installment')),
                ('installment_ref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='credit.installmentrefinancing')),
                ('mov', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cashregister.movement')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
