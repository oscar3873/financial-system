from django.db import models
from django.forms import ValidationError
from django.db.models.signals import post_save, post_delete, pre_save, post_init
from django.contrib.auth.models import User
import math

from django.shortcuts import redirect

# Create your models here.
class CashRegister(models.Model):
    
    total_balanceARS = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    total_balanceUSD = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    total_balanceEUR = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    total_balanceTRANSFER = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    total_balanceCREDITO = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    total_balanceDEBITO = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    
    #Name of the admin site
    def __str__(self) -> str:
        return "Caja"
    
    # def save(self, *args, **kwargs):
        
    #     #Total balance calculation
    #     #ARS
    #     listMovARS = list(self.movement_cash.filter(money_type='PESO'))
    #     listARS = [float(mov.amount) for mov in listMovARS]
    #     self.total_balanceARS = math.fsum(listARS)
    #     #USD
    #     listMovUSD = list(self.movement_cash.filter(money_type='USD'))
    #     listUSD = [float(mov.amount) for mov in listMovUSD]
    #     self.total_balanceUSD = math.fsum(listUSD)
    #     #EUR
    #     listMovEUR = list(self.movement_cash.filter(money_type='EUR'))
    #     listEUR = [float(mov.amount) for mov in listMovEUR]
    #     self.total_balanceEUR = math.fsum(listEUR)
    #     #TRANSFER
    #     listMovTRANSFER = list(self.movement_cash.filter(money_type='TRANSFER'))
    #     listTRANSFER = [float(mov.amount) for mov in listMovTRANSFER]
    #     self.total_balanceTRANSFER = math.fsum(listTRANSFER)
    #     #CREDITO
    #     listMovCREDITO = list(self.movement_cash.filter(money_type='CREDITO'))
    #     listCREDITO = [float(mov.amount) for mov in listMovCREDITO]
    #     self.total_balanceCREDITO = math.fsum(listCREDITO)
    #     #DEBITO
    #     listMovDEBITO = list(self.movement_cash.filter(money_type='DEBITO'))
    #     listDEBITO = [float(mov.amount) for mov in listMovDEBITO]
    #     self.total_balanceDEBITO = math.fsum(listDEBITO)
        
        
        
    #     #Unique instance of the register cash    
    #     # if not self.pk and CashRegister.objects.exists():
    #     # # if you'll not check for self.pk 
    #     # # then error will also raised in update of exists model
    #     #     raise ValidationError('There is can be only one CashRegister instance')
    #     return super(CashRegister, self).save(*args, **kwargs)
    
class Movement(models.Model):
    
    OPERATION_CHOISE = (
        ('Ingreso', 'Ingreso'),
        ('Egreso', 'Egreso')
    )
    
    MONEY_TYPE = (
        ('PESO', 'PESO'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRANSFER', 'TRANSFER'),
        ('CREDITO', 'CREDITO'),
        ('DEBITO', 'DEBITO'),
    )
    
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Amount of transaction")
    cashregister = models.ForeignKey(CashRegister, on_delete=models.CASCADE, help_text="Cash register", related_name="cash")
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, null=True, help_text="Usuario Operator", related_name="user_movements")
    operation_mode = models.CharField(max_length=10, choices=OPERATION_CHOISE, help_text="Operation mode")
    description = models.TextField(blank=True, max_length=500, help_text="description of the operation")
    money_type = models.CharField(max_length=20, choices=MONEY_TYPE, help_text="money type")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def all_properties(self):
        return ["Monto","Tipo de Operacion","Descripcion","Tipo de Divisa","Fecha de Realizacion","Por"]
    
    def __str__(self):
        return "Operacion #{}".format(self.pk)
    
    
def refresh_cashregister(instance, *args, **kwargs):
    #Total balance calculation
    #ARS
    listMovARS = list(instance.cashregister.cash.filter(money_type='PESO'))
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

    instance.amount = abs(instance.amount)
    if instance.operation_mode == 'Egreso':
        instance.amount = -instance.amount

pre_save.connect(operation_type_validate, sender=Movement)
post_save.connect(refresh_cashregister, sender= Movement)
post_delete.connect(refresh_cashregister, sender= Movement)