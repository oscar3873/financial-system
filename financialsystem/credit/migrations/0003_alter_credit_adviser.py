# Generated by Django 4.1.5 on 2023-04-27 19:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adviser', '0001_initial'),
        ('credit', '0002_alter_credit_adviser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credit',
            name='adviser',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adviser.adviser'),
        ),
    ]
