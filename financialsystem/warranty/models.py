from django.db import models

# Create your models here.
from django.db import models
from credit.models import Credit
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
    
    article = models.CharField(max_length=50, help_text="Articulo", verbose_name="Articulo")
    purchase_papers = models.BooleanField(blank=True, verbose_name="Papeles de compra", default=False, help_text="Papeles de compra")
    brand = models.CharField(max_length=50, help_text="Marca", verbose_name="Marca")
    model = models.CharField(max_length=50, help_text="Modelo", verbose_name="Modelo")
    accessories = models.CharField(max_length=50, help_text="Accesorios", verbose_name="Accesorios")
    state = models.CharField(blank=True, choices=ARTICLE_STATE, max_length=30, verbose_name="Estado")
    credit = models.ForeignKey(Credit, on_delete=models.SET_NULL, blank=True, null=True, default=None, help_text="Empeño del usuario", related_name="warranty_clients")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.article + " " + self.brand + " " + self.model
    
    class Meta:
        ordering = ["created_at"]