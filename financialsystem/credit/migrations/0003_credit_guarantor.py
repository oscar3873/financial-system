# Generated by Django 4.1.5 on 2023-04-02 23:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guarantor', '0003_remove_guarantor_credit'),
        ('credit', '0002_credit_has_pay_stub'),
    ]

    operations = [
        migrations.AddField(
            model_name='credit',
            name='guarantor',
            field=models.ForeignKey(blank=True, default=None, help_text='Cliente del Credito', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='credits_g', to='guarantor.guarantor'),
        ),
    ]