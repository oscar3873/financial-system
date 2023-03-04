from decimal import Decimal
import uuid
from django.db import models
from clients.models import Client
from cashregister.models import Movement
from django.db.models.signals import post_save, pre_save
from datetime import datetime, timedelta
# Create your models here.
#CREDITO

class Credit(models.Model):
    CHOICE = [
        ('Pagado', 'Pagado'),
        ('A Tiempo','A Tiempo'),
        ('Legales','Legales'),
        ]

    is_active = models.BooleanField(default=False)
    is_paid_credit = models.BooleanField(default=False, help_text="El credito esta pagado")
    is_old_credit = models.BooleanField(default=False, help_text="Es un credito antiguo")
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    condition = models.CharField(max_length=15,choices=CHOICE, default='A Tiempo')
    credit_interest = models.PositiveIntegerField(default=40, help_text="Intereses de credito")
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto del Credito")
    mov = models.OneToOneField(Movement,on_delete=models.SET_NULL,null=True)
    credit_repayment_amount = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=15, help_text="Monto de Devolucion del Credito")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True, default=None, help_text="Cliente del Credito", related_name="client_credits")
    installment_num = models.PositiveIntegerField(default=1, null=True, help_text="Numeros de Cuotas")
    start_date = models.DateTimeField(verbose_name='Fecha de Inicio',default=datetime.now, null=True)
    end_date = models.DateTimeField(verbose_name='Fecha de Finalizacion del Credito', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        
        if self.client:
            return "Credito de {}, {}".format(self.client.first_name, self.client.last_name)
        else:
            return super().__str__()
            
            
#CUOTA DE CREDITO
class Installment(models.Model):
    CONDITION = [
        ('Pagada', 'Pagada'),
        ('Refinanciada','Refinanciada'),
        ('Vencida','Vencida'),
        ('A Tiempo','A Tiempo')
        ]

    is_caduced_installment = models.BooleanField(default=False , help_text="La cuota esta vencida")
    is_paid_installment = models.BooleanField(default=False, help_text="La cuota esta pagada")
    is_refinancing_installment = models.BooleanField(default=False, help_text="La cuota fue refinanciada")
    
    installment_number = models.PositiveSmallIntegerField(help_text="Numero de cuota del credito")
    daily_interests = models.DecimalField(blank=False, decimal_places=2, max_digits=20, null=True, default=0, help_text="Intereses diarios")
    start_date = models.DateTimeField(default=datetime.now, null=True)
    end_date = models.DateTimeField(null=True)
    condition = models.CharField(max_length=15,choices=CONDITION, default='A Tiempo')
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name="installment", help_text="Credito de la cuota")
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto de la cuota")
    lastup = models.DateTimeField(default=datetime.now, null=True) #PARA CALCULO DE INTERESES DIARIOS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return "Cuota {} del {}".format(self.installment_number, self.credit)

    class Meta:
        ordering = ['created_at']

#REFINANCIACION   
class Refinancing(models.Model):
    
    is_paid_refinancing = models.BooleanField(default=False, help_text="La refinanciacion esta pagada")
    
    refinancing_interest = models.PositiveIntegerField(default=48, help_text="Intereses de la refinanciacion")
    amount = models.DecimalField(decimal_places=2, max_digits=15)
    refinancing_repayment_amount = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=15, help_text="Monto de Devolver de la Refinanciacion")
    installment = models.OneToOneField(Installment, on_delete=models.CASCADE, blank=True, null=True, default=None, help_text="Cuota de la Refinanciacion", related_name="refinancing")
    installment_num_refinancing = models.PositiveIntegerField(default=1, null=True, help_text="Numeros de Cuotas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return "Refinanciacion de la {}".format(self.installment)
        
#CUOTA DE REFINANCIACION
class InstallmentRefinancing(models.Model):
    CHOICE = [
        ('Pagado', 'Pagado'),
        ('A Tiempo','A Tiempo'),
        ('Legales','Legales'),
        ]

    is_caduced_installment = models.BooleanField(default=False , help_text="La cuota esta vencida")
    is_paid_installment = models.BooleanField(default=False, help_text="La cuota esta pagada")
    
    condition = models.CharField(max_length=15,choices=CHOICE, default='A Tiempo')
    installment_number = models.PositiveSmallIntegerField(help_text="Numero de cuota de la refinanciacion")
    refinancing = models.ForeignKey(Refinancing, on_delete=models.CASCADE, related_name="installment_refinancing", help_text="Refinanciacion de la cuota")
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto de la cuota de refinanciacion")
    payment_date = models.DateField(help_text="Fecha de pago de la cuota de refinanciacion")
    start_date = models.DateTimeField(default=datetime.now, verbose_name='Fecha de Inicio')
    end_date = models.DateTimeField(verbose_name='Fecha de Vencimiento',blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return "Cuota {} de la {}".format(self.installment_number, self.refinancing)

#-------------------- SEÑALES PARA CREDITOS Y CUOTAS --------------------
def repayment_amount_auto(instance, *args, **kwargs):
        credit = instance
        credit.end_date = (timedelta(days=30)*credit.installment_num) + credit.start_date
        repayment_amount = credit.installment_num*(Decimal(credit.credit_interest/100)*credit.amount)/(1-pow((1+Decimal(credit.credit_interest/100)),(- credit.installment_num)))
        credit.credit_repayment_amount = Decimal(repayment_amount)

def create_installments_auto(instance, created, *args, **kwargs):
    if not instance.is_old_credit:
        if not created:
            instance.installment.all().delete()
        credit = instance
        days = 30
        amount_installment = Decimal(credit.credit_repayment_amount/credit.installment_num)
        for numberInstallments in range(credit.installment_num):
            end_date = credit.start_date + timedelta(days=days)
            numberInstms = numberInstallments + 1
            credit.installment.create(
                installment_number=numberInstms, 
                start_date = credit.start_date,
                credit= credit, 
                amount= amount_installment, 
                end_date=end_date
                )
            days += 30

pre_save.connect(repayment_amount_auto, sender= Credit)
post_save.connect(create_installments_auto, sender= Credit)


#-------------------- SEÑALES PARA REFINANCIACION Y CUOTAS --------------------
def refinancing_repayment_amount_auto(instance, *args, **kwargs):
    refinancing = instance

    match (int (refinancing.installment_num_refinancing)):
        case 3: refinancing.refinancing_interest = 25
        case 6: refinancing.refinancing_interest = 50
        case 9: refinancing.refinancing_interest = 75
        case _: refinancing.refinancing_interest = 100
    
    print((refinancing.amount))
    interests_amount = Decimal(float(refinancing.amount) * (float(refinancing.refinancing_interest+100) / 100))
    repayment_amount = refinancing.amount + interests_amount
    refinancing.refinancing_repayment_amount = Decimal(repayment_amount)

def create_installmentsR_auto(instance, created, *args, **kwargs):
    if created:
        refinancing = instance
        days = 30
        amount_installment = Decimal(refinancing.refinancing_repayment_amount/refinancing.installment_num_refinancing)
        for numberInstallments in range(refinancing.installment_num_refinancing):
            payment_date = instance.created_at + timedelta(days=days)
            numberInstms = numberInstallments + 1
            refinancing.installment_refinancing.create(installment_number=numberInstms, refinancing= refinancing, amount=amount_installment, payment_date=payment_date)
            days += 30

pre_save.connect(refinancing_repayment_amount_auto, sender= Refinancing)
post_save.connect(create_installmentsR_auto, sender= Refinancing)