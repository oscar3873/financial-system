# Generated by Django 4.1.5 on 2023-04-04 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('adviser', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True, verbose_name='Titulo de la nota')),
                ('content', models.TextField(blank=True, max_length=250, null=True, verbose_name='Contenido de la nota')),
                ('color', models.CharField(blank=True, help_text='Color de la nota', max_length=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, default=None, help_text='Notas de Usuario', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_notes', to='adviser.adviser')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
