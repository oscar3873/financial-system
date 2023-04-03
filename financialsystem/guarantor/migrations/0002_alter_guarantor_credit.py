# Generated by Django 4.1.5 on 2023-04-02 21:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0002_credit_has_pay_stub'),
        ('guarantor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guarantor',
            name='credit',
            field=models.ForeignKey(blank=True, help_text='Garantia del Credito', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='guarantor_client', to='credit.credit'),
        ),
    ]