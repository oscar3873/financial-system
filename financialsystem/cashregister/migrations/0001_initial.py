# Generated by Django 4.1.5 on 2023-02-03 04:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CashRegister",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "total_balanceARS",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
                ),
                (
                    "total_balanceUSD",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
                ),
                (
                    "total_balanceEUR",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
                ),
                (
                    "total_balanceTRANSFER",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Movement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Amount of transaction",
                        max_digits=8,
                    ),
                ),
                (
                    "operation_mode",
                    models.CharField(
                        choices=[("I", "Ingreso"), ("E", "Egreso")],
                        help_text="Operation mode",
                        max_length=10,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="description of the operation",
                        max_length=500,
                    ),
                ),
                (
                    "money_type",
                    models.CharField(
                        choices=[
                            ("PESO", "PESO"),
                            ("USD", "USD"),
                            ("EUR", "EUR"),
                            ("TRANSFER", "TRANSFER"),
                        ],
                        help_text="money type",
                        max_length=20,
                    ),
                ),
                (
                    "cashregister",
                    models.ForeignKey(
                        help_text="Cash register",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="movement_cash",
                        to="cashregister.cashregister",
                    ),
                ),
            ],
        ),
    ]