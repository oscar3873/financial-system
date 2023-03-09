from datetime import datetime
from decimal import Decimal
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save


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
@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, **kwargs):
    if kwargs.get('created', False):
        Adviser.objects.get_or_create(user = instance)
        print("Se acaba de crear un usuario y un asesor")

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
    type = models.CharField(max_length=20, null=True,choices=REG)
    money_type = models.CharField(max_length=20 , null=True, choices=MONEY_TYPE, default= MONEY_TYPE[0])
    last_up = models.DateTimeField(default=datetime.now)
    detail = models.TextField(max_length=100, null=True, blank=True, help_text="Detalle de la operacion")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

#-------------------------- SEÑALES PARA COMMISSION --------------------------------------
def update_commission(instance, *args, **kwargs):
    if instance.is_paid:
        match (float(instance._last_interest)):
            case 7.5: porcentage = instance._last_interest
            case 5: porcentage = instance._last_interest
            case _: porcentage = instance._last_interest

        real_value = Decimal((instance.amount*100)/instance.interest)
        print(real_value, instance._last_interest)
        instance.amount = Decimal(real_value*(instance._last_interest/100))
        instance.interest = Decimal(porcentage)
        instance.last_up = datetime.now()

pre_save.connect(update_commission, sender=Comission)