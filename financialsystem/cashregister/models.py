import uuid
import math

from django.db import models
from djmoney.models.fields import MoneyField
from django.db.models.signals import post_save, post_delete, pre_save
from adviser.models import Adviser
from decimal import Decimal, ROUND_HALF_EVEN

from core.utils import round_to_nearest_hundred


# from adviser.models import Adviser

# Create your models here.
class CashRegister(models.Model):
    
    total_balanceARS = MoneyField(max_digits=20, decimal_places=2 , default_currency='ARS', null=True, default=0)
    total_balanceUSD = MoneyField(max_digits=20, decimal_places=2 , default_currency='USD', null=True, default=0)
    total_balanceEUR = MoneyField(max_digits=20, decimal_places=2 , default_currency='EUR', null=True, default=0)
    total_balanceTRANSFER = MoneyField(max_digits=20, decimal_places=2 , default_currency='ARS', null=True, default=0)
    total_balanceCREDITO = MoneyField(max_digits=20, decimal_places=2 , default_currency='ARS', null=True, default=0)
    total_balanceDEBITO = MoneyField(max_digits=20, decimal_places=2 , default_currency='ARS', null=True, default=0)
    auth_expenses = models.CharField(max_length = 128, blank=True, default='123')
    
    #Name of the admin site
    def __str__(self) -> str:
        return "Caja"
    
    
class Movement(models.Model):
    OPERATION_CHOISE = (
        ('INGRESO', 'INGRESO'),
        ('EGRESO', 'EGRESO')
    )
    
    MONEY_TYPE = (
        ('PESOS', 'PESOS'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRANSFER', 'TRANSFER'),
        ('CREDITO', 'CREDITO'),
        ('DEBITO', 'DEBITO'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Amount of transaction")
    cashregister = models.ForeignKey(CashRegister, on_delete=models.CASCADE, help_text="Cash register", related_name="cash")
    user = models.ForeignKey(Adviser, on_delete=models.SET_NULL, default=None, null=True, help_text="Usuario Operator", related_name="user_movements")
    operation_mode = models.CharField(max_length=10, choices=OPERATION_CHOISE, help_text="Operation mode")
    description = models.TextField(blank=True, max_length=500, help_text="description of the operation")
    money_type = models.CharField(max_length=20, choices=MONEY_TYPE, help_text="Tipo de divisa")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "Operacion #{}".format(self.pk)

    class Meta:
        ordering = ['-created_at']

    
def refresh_cashregister(instance, *args, **kwargs):
    #Total balance calculation
    #ARS
    listMovARS = list(instance.cashregister.cash.filter(money_type='PESOS'))
    listARS = [float(mov.amount) for mov in listMovARS]
    instance.cashregister.total_balanceARS = math.fsum(listARS)
    #USD
    listMovUSD = list(instance.cashregister.cash.filter(money_type='USD'))
    listUSD = [float(mov.amount) for mov in listMovUSD]
    instance.cashregister.total_balanceUSD = math.fsum(listUSD)
    #EUR
    listMovEUR = list(instance.cashregister.cash.filter(money_type='EUR'))
    listEUR = [float(mov.amount) for mov in listMovEUR]
    instance.cashregister.total_balanceEUR = math.fsum(listEUR)
    #TRANSFER
    listMovTRANSFER = list(instance.cashregister.cash.filter(money_type='TRANSFER'))
    listTRANSFER = [float(mov.amount) for mov in listMovTRANSFER]
    instance.cashregister.total_balanceTRANSFER = math.fsum(listTRANSFER)
    #CREDITO
    listMovCREDITO = list(instance.cashregister.cash.filter(money_type='CREDITO'))
    listCREDITO = [float(mov.amount) for mov in listMovCREDITO]
    instance.cashregister.total_balanceCREDITO = math.fsum(listCREDITO)
    #DEBITO
    listMovDEBITO = list(instance.cashregister.cash.filter(money_type='DEBITO'))
    listDEBITO = [float(mov.amount) for mov in listMovDEBITO]
    instance.cashregister.total_balanceDEBITO = math.fsum(listDEBITO)

    instance.cashregister.save()


def operation_type_validate(instance, *args, **kwargs):
    """
    Verifica la existencia de una Caja, caso contrario, es creada.
    """
    if not CashRegister.objects.exists():
        instance.cashregister = CashRegister.objects.create()
    instance.amount = abs(instance.amount)
    if instance.operation_mode == 'EGRESO':
        instance.amount = -instance.amount


pre_save.connect(operation_type_validate, sender=Movement)
post_save.connect(refresh_cashregister, sender= Movement)
post_delete.connect(refresh_cashregister, sender= Movement)