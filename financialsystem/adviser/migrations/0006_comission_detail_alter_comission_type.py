# Generated by Django 4.1.7 on 2023-02-28 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adviser', '0005_alter_comission_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='comission',
            name='detail',
            field=models.TextField(blank=True, help_text='Detalle de la operacion', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='comission',
            name='type',
            field=models.CharField(choices=[('REGISTRO', 'REGISTRO'), ('COBRO', 'COBRO')], max_length=20, null=True),
        ),
    ]
