from datetime import datetime
from decimal import Decimal
import uuid

from django.db.models.signals import post_save, pre_save, post_delete
from django.db import models

from credit.models import Installment, InstallmentRefinancing
from cashregister.models import CashRegister, Movement
from adviser.models import Comission, Adviser


# Create your models here.
class Payment(models.Model):
    MONEY_TYPE = (
        ('PESOS', 'PESOS'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRANSFER', 'TRANSFER'),
        ('CREDITO', 'CREDITO'),
        ('DEBITO', 'DEBITO'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(help_text="Monto de Pago", default=0,max_digits=15,decimal_places=2)
    payment_date = models.DateTimeField(default=datetime.now, help_text="Fecha de Pago")
    adviser = models.ForeignKey(Adviser, on_delete=models.SET_NULL, null=True, blank=True)
    commission_to = models.OneToOneField(Comission, on_delete=models.SET_NULL, null=True, blank=True)
    payment_mov = models.OneToOneField(Movement, on_delete=models.CASCADE, null=True, blank=True)
    payment_method = models.CharField(max_length=20,choices=MONEY_TYPE, help_text="Metodo de Pago")
    detail = models.CharField(max_length=150, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        if self.detail:
            return "PAGO: {}".format(self.detail)
        else:
            return super().__str__()

    class Meta:
        ordering = ["created_at"]


#--------------------------- SEÑALES PARA PAYMENT -------------------------------------
def up_installment(instance, *args, **kwargs):
    """
    Crea un movimiento luego de guardar el objeto Payment.
    """
    instance.payment_mov = Movement.objects.create(
            amount = instance.amount,
            user = instance.adviser,
            cashregister = CashRegister.objects.last(),
            operation_mode = 'INGRESO',
            description= instance.detail,
            money_type = instance.payment_method
            )
    comission_create_inst(instance)


def comission_create_inst(instance):
    """
    Crea un comission luego de guardar el objeto Payment.
    """
    amount = instance.amount*Decimal(0.05)

    instance.commission_to = Comission.objects.create(
            adviser = instance.adviser,
            amount = amount,
            interest = Decimal(5),
            type = 'COBRO',
            operation_amount = instance.amount,
            last_up = instance.payment_date,
            money_type = instance.payment_method,
            detail= instance.detail,
        )

def delete_commission(instance, *args, **kwargs):
    instance.commission_to.delete()

pre_save.connect(up_installment, sender = Payment)
post_delete.connect(delete_commission, sender = Payment)
