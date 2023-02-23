# Generated by Django 4.1.7 on 2023-02-23 01:06

from decimal import Decimal
from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cashregister', '0003_alter_cashregister_total_balancears'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashregister',
            name='total_balanceCREDITO',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='ARS', max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='cashregister',
            name='total_balanceDEBITO',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='ARS', max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='cashregister',
            name='total_balanceEUR',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='EUR', max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='cashregister',
            name='total_balanceTRANSFER',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='ARS', max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='cashregister',
            name='total_balanceUSD',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='USD', max_digits=20, null=True),
        ),
    ]
