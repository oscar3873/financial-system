from django.db import models
from django.forms import ValidationError
from django.db.models.signals import post_save, post_delete, pre_save

# Create your models here.
class CashRegister(models.Model):
    
    total_balanceARS = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    total_balanceUSD = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    total_balanceEUR = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    total_balanceTRANSFER = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    
    #Name of the admin site
    def __str__(self) -> str:
        return "Caja Registradora"
    
    def save(self, *args, **kwargs):
        
        #Total balance calculation
        #ARS
        listMovARS = list(self.movement_cash.filter(money_type='PESO'))
        listARS = [int(mov.amount) for mov in listMovARS]
        self.total_balanceARS = sum(listARS)
        #USD
        listMovUSD = list(self.movement_cash.filter(money_type='USD'))
        listUSD = [int(mov.amount) for mov in listMovUSD]
        self.total_balanceUSD = sum(listUSD)
        #EUR
        listMovEUR = list(self.movement_cash.filter(money_type='EUR'))
        listEUR = [int(mov.amount) for mov in listMovEUR]
        self.total_balanceEUR = sum(listEUR)
        #TRANSFER
        listMovTRANSFER = list(self.movement_cash.filter(money_type='TRANSFER'))
        listTRANSFER = [int(mov.amount) for mov in listMovTRANSFER]
        self.total_balanceTRANSFER = sum(listTRANSFER)
        
        #Unique instance of the register cash    
        # if not self.pk and CashRegister.objects.exists():
        # # if you'll not check for self.pk 
        # # then error will also raised in update of exists model
        #     raise ValidationError('There is can be only one CashRegister instance')
        return super(CashRegister, self).save(*args, **kwargs)
    
class Movement(models.Model):
    
    OPERATION_CHOISE = (
        ('I', 'Ingreso'),
        ('E', 'Egreso')
    )
    
    MONEY_TYPE = (
        ('PESO', 'PESO'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRANSFER', 'TRANSFER')
    )
    
    amount = models.DecimalField(decimal_places=2, max_digits=8, help_text="Amount of transaction")
    cashregister = models.ForeignKey(CashRegister, on_delete=models.CASCADE, help_text="Cash register", related_name="movement_cash")
    operation_mode = models.CharField(max_length=10, choices=OPERATION_CHOISE, help_text="Operation mode")
    description = models.TextField(blank=True, max_length=500, help_text="description of the operation")
    money_type = models.CharField(max_length=20, choices=MONEY_TYPE, help_text="money type")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
def refresh_cashregister(instance, *args, **kwargs):
    instance.cashregister.save()

def operation_type_validate(instance, *args, **kwargs):
    instance.amount = abs(instance.amount)
    if instance.operation_mode == 'E':
        instance.amount = -instance.amount

pre_save.connect(operation_type_validate, sender=Movement)
post_save.connect(refresh_cashregister, sender= Movement)
post_delete.connect(refresh_cashregister, sender= Movement)