from decimal import Decimal
import math
from django.db import models
from clients.models import Client
from django.db.models.signals import post_save, post_delete, pre_save
import datetime

# Create your models here.
#CREDITO

class Credit(models.Model):
    
    is_active = models.BooleanField(default=False)
    is_paid_credit = models.BooleanField(default=False, help_text="El credito esta pagado")
    is_old_credit = models.BooleanField(default=False, help_text="Es un credito antiguo")
    
    credit_interest = models.PositiveIntegerField(default=40, help_text="Intereses de credito")
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto del Credito")
    credit_repayment_amount = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=15, help_text="Monto de Devolucion del Credito")
    client = models.ForeignKey(Client, on_delete=models.SET_DEFAULT, blank=True, null=True, default=None, help_text="Cliente del Credito", related_name="client_credits")
    number_installment = models.PositiveIntegerField(default=1, null=True, help_text="Numeros de Cuotas")
    created = models.DateTimeField(default=datetime.datetime.now, null=True, help_text="Cuando fue otorgado el credito")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        
        if self.client:
            return "Credito de {}, {}".format(self.client.first_name, self.client.last_name)
        else:
            return super().__str__()
#CUOTA DE CREDITO
class Installment(models.Model):
    
    is_caduced_installment = models.BooleanField(default=False , help_text="La cuota esta vencida")
    is_paid_installment = models.BooleanField(default=False, help_text="La cuota esta pagada")
    is_refinancing_installment = models.BooleanField(default=False, help_text="La cuota fue refinanciada")
    
    installment_number = models.PositiveSmallIntegerField(help_text="Numero de cuota del credito")
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name="installment", help_text="Credito de la cuota")
    amount_installment = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto de la cuota")
    payment_date = models.DateField(help_text="Fecha de pago de la cuota")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return "Cuota {} del {}".format(self.installment_number, self.credit)
#REFINANCIACION   
class Refinancing(models.Model):
    
    is_paid_refinancing = models.BooleanField(default=False, help_text="La refinanciacion esta pagada")
    
    refinancing_interest = models.PositiveIntegerField(default=48, help_text="Intereses de la refinanciacion")
    amount_refinancing = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto a refinanciar")
    refinancing_repayment_amount = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=15, help_text="Monto de Devolver de la Refinanciacion")
    installment = models.OneToOneField(Installment, on_delete=models.CASCADE, blank=True, null=True, default=None, help_text="Cuota de la Refinanciacion", related_name="refinancing")
    number_installment_refinancing = models.PositiveIntegerField(default=1, null=True, help_text="Numeros de Cuotas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return "Refinanciacion de la {}".format(self.installment)
#CUOTA DE REFINANCIACION
class InstallmentRefinancing(models.Model):
    is_caduced_installment = models.BooleanField(default=False , help_text="La cuota esta vencida")
    is_paid_installment = models.BooleanField(default=False, help_text="La cuota esta pagada")
    
    installment_number = models.PositiveSmallIntegerField(help_text="Numero de cuota de la refinanciacion")
    refinancing = models.ForeignKey(Refinancing, on_delete=models.CASCADE, related_name="installment_refinancing", help_text="Refinanciacion de la cuota")
    amount_installment = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto de la cuota de refinanciacion")
    payment_date = models.DateField(help_text="Fecha de pago de la cuota de refinanciacion")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return "Cuota {} de la {}".format(self.installment_number, self.refinancing)

#-------------------- SEÑALES PARA CREDITOS Y CUOTAS --------------------
def repayment_amount_auto(instance, *args, **kwargs):

        credit = instance
        interests_amount = Decimal(float(credit.amount) * (float(credit.credit_interest) / 100))/ Decimal(1 - pow((1+Decimal(float(credit.credit_interest) / 100)), -credit.number_installment))
        repayment_amount = credit.amount + interests_amount
        credit.credit_repayment_amount = Decimal(repayment_amount)

def create_installments_auto(instance, created, *args, **kwargs):

    if created:
        credit = instance
        days = 30
        amount_installment = Decimal(credit.credit_repayment_amount/credit.number_installment)
        for numberInstallments in range(credit.number_installment):
            payment_date = instance.created_at + datetime.timedelta(days=days)
            numberInstms = numberInstallments + 1
            credit.installment.create(installment_number=numberInstms, credit= credit, amount_installment= amount_installment, payment_date=payment_date)
            days += 30
pre_save.connect(repayment_amount_auto, sender= Credit)
post_save.connect(create_installments_auto, sender= Credit)

#-------------------- SEÑALES PARA REFINANCIACION Y CUOTAS --------------------
def refinancing_repayment_amount_auto(instance, *args, **kwargs):

        refinancing = instance
        interests_amount = Decimal(float(refinancing.amount_refinancing) * (float(refinancing.refinancing_interest) / 100))
        repayment_amount = refinancing.amount_refinancing + interests_amount
        refinancing.refinancing_repayment_amount = Decimal(repayment_amount)

def create_installments_auto(instance, created, *args, **kwargs):

    if created:
        refinancing = instance
        days = 30
        amount_installment = Decimal(refinancing.refinancing_repayment_amount/refinancing.number_installment_refinancing)
        for numberInstallments in range(refinancing.number_installment_refinancing):
            payment_date = instance.created_at + datetime.timedelta(days=days)
            numberInstms = numberInstallments + 1
            refinancing.installment_refinancing.create(installment_number=numberInstms, refinancing= refinancing, amount_installment=amount_installment, payment_date=payment_date)
            days += 30
pre_save.connect(refinancing_repayment_amount_auto, sender= Refinancing)
post_save.connect(create_installments_auto, sender= Refinancing)