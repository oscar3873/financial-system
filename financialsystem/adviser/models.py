from datetime import datetime
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


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
        ('COBRO','COBRO')
        ]

    is_paid = models.BooleanField(default=False)
    adviser = models.ForeignKey(Adviser,on_delete=models.SET_NULL,null=True)
    amount = models.DecimalField(blank=False, decimal_places=2, max_digits=20)
    type = models.CharField(max_length=20, null=True,choices=REG)
    money_type = models.CharField(max_length=20 , null=True, choices=MONEY_TYPE, default= MONEY_TYPE[0])
    create_date = models.DateTimeField(default=datetime.now)
    detail = models.TextField(max_length=50, null=True, blank=True, help_text="Detalle de la operacion")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']