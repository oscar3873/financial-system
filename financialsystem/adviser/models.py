from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from cashregister.models import Movement

# Create your models here.
class Adviser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="adviser")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return "{}, {}".format(self.user.first_name, self.user.last_name)
    
# signals
@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, **kwargs):
    if kwargs.get('created', False):
        Adviser.objects.get_or_create(user = instance)
        print("Se acaba de crear un usuario y un asesor")

###############################################################################

class Comission(models.Model):
    REG = [
        ('REGISTRO','REGISTRO'),
        ('COBRO','COBRO')
        ]

    adviser = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    amount = models.DecimalField(blank=False, decimal_places=2, max_digits=20)
    c_type = models.CharField(max_length=20, null=True,choices=REG, default='Registro')
    create_date = models.DateTimeField(default=datetime.now)
    mov = models.OneToOneField(Movement, on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)