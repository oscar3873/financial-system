from datetime import datetime
from decimal import Decimal
from django.db import models
from django.db.models.signals import pre_save, post_delete, post_save

# Create your models here.
from django.db import models
from credit.models import Credit
from adviser.models import Adviser, Comission
from cashregister.models import Movement, CashRegister
# Create your models here.

class Warranty(models.Model):
    
    ARTICLE_STATE = (
        ('NUEVO','NUEVO'),
        ('USADO:COMO NUEVO', 'USADO:COMO NUEVO'),
        ('USADO:MUY BUENO', 'USADO:MUY BUENO'),
        ('USADO:BUENO', 'USADO:BUENO'),
        ('USADO:ACEPTABLE', 'USADO:ACEPTABLE'),
        ('USADO:REACONDICIONADO', 'USADO:REACONDICIONADO'),
        ('USADO:MUCHO USO', 'USADO:MUCHO USO'),
    )
    
    is_selled = models.BooleanField(default=False)

    article = models.CharField(max_length=50, help_text="Articulo", verbose_name="Articulo")
    purchase_papers = models.BooleanField(blank=True, verbose_name="Papeles de compra", default=False, help_text="Papeles de compra")
    brand = models.CharField(max_length=50, help_text="Marca", verbose_name="Marca")
    model = models.CharField(max_length=50, help_text="Modelo", verbose_name="Modelo")
    accessories = models.CharField(max_length=50, help_text="Accesorios", verbose_name="Accesorios")
    state = models.CharField(blank=True, choices=ARTICLE_STATE, max_length=30, verbose_name="Estado")
    credit = models.ForeignKey(Credit, on_delete=models.SET_NULL, blank=True, null=True, default=None, help_text="Empeño del usuario", related_name="warranty_clients")
    detail = models.TextField(max_length=150, blank=True, null=True, help_text="Observaciones del articulo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.article + " " + self.brand + " " + self.model
    
    class Meta:
        ordering = ["created_at"]


class Sell(models.Model):
    MONEY_TYPE = [
        ('PESOS','PESOS'),
        ('USD','USD'),
        ('EUR', 'EUR'),
        ('TRANSFER','TRANSFERENCIA'),
        ('DEBITO','DEBITO'),
        ('CREDITO','CREDITO'),
        ]

    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(max_length=15, choices=MONEY_TYPE,null=True, blank=True, default='PESOS')
    adviser = models.ForeignKey(Adviser,on_delete=models.SET_NULL, null=True)
    commission = models.ForeignKey(Comission, on_delete=models.SET_NULL, null=True, blank=True)
    article = models.OneToOneField(Warranty, on_delete=models.SET_NULL, blank=True, null=True, related_name='sell')
    mov = models.ForeignKey(Movement, on_delete=models.CASCADE, blank=True, null=True)
    sell_date = models.DateTimeField(null=True, default=datetime.now)
    detail = models.TextField(max_length=150, blank=True, null=True, help_text="Observaciones del articulo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

#--------------------------------------- SEÑALES PARA SELL ------------------------------------------------

def sell_commission(instance, *args, **kwargs):
    """
    Crea una comision por venta.
    """
    if not instance.commission:
        amount = instance.amount*Decimal(0.05)
        instance.commission = Comission.objects.create(
            adviser = instance.adviser,
            interest = Decimal(5),
            amount = amount,
            operation_amount = instance.amount,
            type = 'VENTA',
            last_up = instance.sell_date,
            detail = 'VENTA DE %s - ASESOR: %s' % (instance.article, instance.adviser),
            )
    if not instance.mov:
        instance.mov = Movement.objects.create(
            user = instance.adviser,
            amount = instance.amount,
            cashregister = CashRegister.objects.first(),
            operation_mode = 'INGRESO',
            description = 'VENTA DE %s - ASESOR: %s' % (instance.article, instance.adviser),
            money_type = instance.payment_method,
            )



def sell_delete(instance, origin=False, *args, **kwargs):
    print(instance.commission)
    if instance.commission:
        instance.commission.delete()
        instance.article.is_selled = False
        instance.article.save()

    if not isinstance(origin,Movement):
        instance.mov.delete()
        instance.article.is_selled = False
        instance.article.save()


pre_save.connect(sell_commission, sender=Sell)
post_delete.connect(sell_delete, sender=Sell)

