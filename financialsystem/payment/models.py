from django.db import models
from credit.models import Installment, InstallmentRefinancing

# Create your models here.
class Payment(models.Model):
    
    is_refinancing_pay = models.BooleanField(default=False)
    
    detaill = models.CharField(max_length=250, blank=True, help_text="Detalle del pago")
    installment = models.OneToOneField(Installment, on_delete=models.SET_DEFAULT, blank=True, null=True, default=None, help_text="Cuota que se esta pagando", related_name="installment_pay")
    refinancing = models.OneToOneField(InstallmentRefinancing, on_delete=models.SET_DEFAULT, blank=True, null=True, default=None, help_text="Refinanciacion que se esta pagando", related_name="refinancing_pay")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        
        if self.installment:
            return "Pago de {}".format(self.installment)
        else:
            return super().__str__()
    