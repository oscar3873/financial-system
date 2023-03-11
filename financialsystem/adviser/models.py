from datetime import datetime
from decimal import Decimal
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save, pre_delete

from cashregister.models import Movement, CashRegister


# Create your models here.
class Adviser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="adviser")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return "{}, {}".format(self.user.first_name, self.user.last_name)
    
    class Meta:
        ordering = ['-created_at']
    
# signals
def ensure_profile_exists(sender, instance, **kwargs):
    if kwargs.get('created', False):
        Adviser.objects.get_or_create(user = instance)
        print("Se acaba de crear un usuario y un asesor")

post_save.connect(ensure_profile_exists, sender=User)

###############################################################################

class Comission(models.Model):
    MONEY_TYPE = [
        ('PESOS','PESOS'),
        ('USD','USD'),
        ('EUR', 'EUR'),
        ('TRANSFER','TRANSFERENCIA'),
        ]
    
    REG = [
        ('REGISTRO','REGISTRO'),
        ('COBRO','COBRO'),
        ('VENTA', 'VENTA')
        ]

    is_paid = models.BooleanField(default=False)

    adviser = models.ForeignKey(Adviser,on_delete=models.SET_NULL,null=True)
    interest = models.DecimalField(null=True, decimal_places=2, max_digits=6)
    amount = models.DecimalField(blank=False, decimal_places=2, max_digits=20)
    operation_amount = models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True) 
    type = models.CharField(max_length=20, null=True,choices=REG)
    money_type = models.CharField(max_length=20 , null=True, choices=MONEY_TYPE, default= MONEY_TYPE[0])
    last_up = models.DateTimeField(default=datetime.now)
    mov = models.OneToOneField(Movement, on_delete=models.CASCADE, null=True, blank=True)
    detail = models.TextField(max_length=100, null=True, blank=True, help_text="Detalle de la operacion")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

#-------------------------- SEÑALES PARA COMMISSION --------------------------------------
def paid_commission(instance, *args, **kwargs):
    '''Actualiza la comisión de una instancia si ha sido pagada. 
    Calcula el valor real de la comisión basado en la última tasa de interés almacenada. 
    Actualiza el monto y la tasa de interés de la instancia, y el tiempo de última actualización.'''

    if instance.is_paid:
        instance.mov = Movement.objects.create(
            user = instance.adviser,
            amount = instance.amount,
            cashregister = CashRegister.objects.last(),
            operation_mode = 'EGRESO',
            description = 'COMISION %s - %s' % (instance.adviser, instance.type),
            money_type= instance.money_type
        )

    
pre_save.connect(paid_commission, sender=Comission)
# pre_delete.connect(delete_commission, sender=Comission)
