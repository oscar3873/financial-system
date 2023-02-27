from datetime import datetime
from decimal import Decimal
from django.db import models
from credit.models import Installment
from cashregister.models import CashRegister, Movement
from adviser.models import Comission, Adviser
from django.db.models.signals import post_save


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
    
    amount = models.PositiveIntegerField(help_text="Monto de Pago")
    paid_date = models.DateTimeField(default=datetime.now, help_text="Fecha de Pago")
    installment = models.ForeignKey(Installment, on_delete=models.SET_NULL, null=True, blank=True)
    adviser = models.ForeignKey(Adviser, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=20,choices=MONEY_TYPE, help_text="Metodo de Pago")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        
        if self.installment:
            return "Pago de {}".format(self.installment)
        else:
            return super().__str__()
    
def up_installmet(instance, *args, **kwargs):
    user = instance._user
    Movement.objects.create(
        amount = user.amount,
        user = user,
        cashregister = CashRegister.objects.last(),
        operation_mode = 'INGRESO',
        description= 'COBRO CUOTA %s - CLIENTE %s - ASESOR %s' % (instance.installment_number, instance.credit.client, user),
        money_type = instance.payment_method
        )
    Payment.objects.create(
        amount = instance.amount,
        installment = instance,
        adviser = user,
        payment_method = instance.payment_method
    )
    comission_create_inst(instance)

def comission_create_inst(instance, *args, **kwargs):
    amount = instance.amount*Decimal(0.05)
    Comission.objects.create(
        adviser = instance.credit.client.adviser,
        amount = amount,
        type = 'COBRO',
        create_date = instance.start_date,
        commission_charged_to = instance.credit.client,
        )

post_save.connect(up_installmet, sender = Payment)