from datetime import datetime
from decimal import Decimal

from django.db.models.signals import post_save, pre_save, pre_delete
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

    is_refinancing_pay = models.BooleanField(default=False)
    
    amount = models.DecimalField(help_text="Monto de Pago", default=0,max_digits=15,decimal_places=2)
    payment_date = models.DateTimeField(default=datetime.now, help_text="Fecha de Pago")
    installment_ref = models.OneToOneField(InstallmentRefinancing, on_delete=models.SET_NULL, null=True, blank=True)
    installment = models.OneToOneField(Installment, on_delete=models.SET_NULL, null=True, blank=True)
    adviser = models.ForeignKey(Adviser, on_delete=models.SET_NULL, null=True, blank=True)
    commission_to = models.ForeignKey(Comission, on_delete=models.SET_NULL, null=True, blank=True)
    payment_mov = models.ForeignKey(Movement, on_delete=models.CASCADE, null=True, blank=True)
    payment_method = models.CharField(max_length=20,choices=MONEY_TYPE, help_text="Metodo de Pago")
    detail = models.CharField(max_length=150, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        if self.installment:
            return "Pago de {}".format(self.installment)
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

def comission_create_inst(instance, *args, **kwargs):
    """
    Crea un comission luego de guardar el objeto Payment.
    """
    amount = instance.amount*Decimal(0.05)

    if instance.installment:
        detail = f'COBRO CUOTA {instance.installment.installment_number} - CLIENTE {instance.installment.credit.client} '
    else:
        print(instance.installment_ref.refinancing)
        detail = f'COBRO CUOTA {instance.installment_ref.installment_number} - CLIENTE {instance.installment_ref.refinancing.installment_ref.last().credit.client} '

    instance.commission_to = Comission.objects.create(
            adviser = instance.adviser,
            amount = amount,
            interest = Decimal(5),
            type = 'COBRO',
            original_amount = instance.amount,
            last_up = instance.payment_date,
            money_type = instance.payment_method,
            detail= detail,
        )

def delete_mov_commission(instance, *args, **kwargs):
    """
    Elimina el movimiento y comision luego antes de borrar el pago.
    """
    if instance.payment_mov:
        instance.payment_mov.delete()

    if instance.commission_to:
        instance.commission_to.delete()

pre_save.connect(up_installment, sender = Payment)
pre_delete.connect(delete_mov_commission, sender = Payment)