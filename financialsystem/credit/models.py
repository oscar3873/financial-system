from decimal import Decimal
import math
from django.db import models
from clients.models import Client
from adviser.models import Comission
from cashregister.models import Movement, CashRegister
from django.db.models.signals import post_save, pre_save
from datetime import datetime, date, timedelta
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
    
    condition = models.CharField(max_length=15,choices=CHOICE, default='A Tiempo')
    credit_interest = models.PositiveIntegerField(default=40, help_text="Intereses de credito")
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto del Credito")
    credit_repayment_amount = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=15, help_text="Monto de Devolucion del Credito")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True, default=None, help_text="Cliente del Credito", related_name="client_credits")
    installment_num = models.PositiveIntegerField(default=1, null=True, help_text="Numeros de Cuotas")
    mov = models.ForeignKey(Movement, on_delete=models.CASCADE, null=True)
    start_date = models.DateTimeField(verbose_name='Fecha de Inicio',default=datetime.now, null=True)
    end_date = models.DateTimeField(verbose_name='Fecha de Finalizacion del Credito', null=True)
    # due_date = models.DateTimeField(verbose_name='Fecha de Vencimiento',blank=True, null=True)
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
    MONEY_TYPE = [
        ('PESOS','PESOS'),
        ('USD','USD'),
        ('EUR', 'EUR'),
        ('TRANSFER','TRANSFERENCIA'),
        ]
        
    is_caduced_installment = models.BooleanField(default=False , help_text="La cuota esta vencida")
    is_paid_installment = models.BooleanField(default=False, help_text="La cuota esta pagada")
    is_refinancing_installment = models.BooleanField(default=False, help_text="La cuota fue refinanciada")
    
    installment_number = models.PositiveSmallIntegerField(help_text="Numero de cuota del credito")
    acc_int = models.DecimalField(blank=False, decimal_places=2, max_digits=20, null=True, default=0)
    start_date = models.DateTimeField(default=datetime.now, null=True)
    end_date = models.DateTimeField(null=True)
    payment_method = models.CharField(max_length=15, choices=MONEY_TYPE,null=True, blank=True)
    condition = models.CharField(max_length=15,choices=CONDITION, default='A Tiempo')
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name="installment", help_text="Credito de la cuota")
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto de la cuota")
    payment_date = models.DateField(help_text="Fecha de pago de la cuota")
    lastup = models.DateTimeField(default=datetime.now, null=True)
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
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto a refinanciar")
    refinancing_repayment_amount = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=15, help_text="Monto de Devolver de la Refinanciacion")
    installment = models.OneToOneField(Installment, on_delete=models.CASCADE, blank=True, null=True, default=None, help_text="Cuota de la Refinanciacion", related_name="refinancing")
    installment_num_refinancing = models.PositiveIntegerField(default=1, null=True, help_text="Numeros de Cuotas")
    mov = models.ForeignKey(Movement, on_delete=models.CASCADE, null=True)
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
        repayment_amount = credit.installment_num*(Decimal(credit.credit_interest/100)*credit.amount)/(1-pow((1+Decimal(credit.credit_interest/100)),(- credit.installment_num)))
        credit.credit_repayment_amount = Decimal(repayment_amount)
        create_movement(credit)


def create_installments_auto(instance, created, *args, **kwargs):
    if created:
        credit = instance
        days = 30
        amount_installment = Decimal(credit.credit_repayment_amount/credit.installment_num)
        for numberInstallments in range(credit.installment_num):
            payment_date = instance.created_at + timedelta(days=days)
            end_date = credit.start_date + timedelta(days=days)*credit.installment_num
            numberInstms = numberInstallments + 1
            credit.installment.create(installment_number=numberInstms, credit= credit, amount= amount_installment, payment_date=payment_date, end_date=end_date)
            days += 30


def create_movement(instance):
    instance.mov = Movement.objects.create(
        user = instance.client.adviser,
        amount = instance.amount,
        cashregister = CashRegister.objects.last(),
        operation_mode = 'EGRESO',
        description = 'CREDITO PARA %s \nCUOTAS: %s' % (instance.client, instance.installment_num),
        money_type = 'PESOS',
        )


def comission_create(instance, *args, **kwargs):
    type = 'REGISTRO'
    comission = 0.075
    amount = instance.amount*Decimal(comission)
    Comission.objects.create(
        adviser = instance.client.adviser,
        amount = amount,
        type = type,
        create_date = instance.start_date,
        commission_charged_to = instance.client,
        )

def up_installmet(instance, created, *args, **kwargs):
    if not created and instance.condition == 'Pagada':
        adviser = instance._adviser
        Movement.objects.create(
            amount = instance.amount,
            user = adviser,
            cashregister = CashRegister.objects.last(),
            operation_mode = 'INGRESO',
            description= 'COBRO CUOTA %s - CLIENTE %s - ASESOR %s' % (instance.installment_number, instance.credit.client, adviser),
            money_type = instance.payment_method
            )
        comission_create_inst(instance)

def comission_create_inst(instance, *args, **kwargs):
    amount = instance.amount*Decimal(0.05)
    Comission.objects.create(
        adviser = instance.credit.client.adviser,
        amount = amount,
        type = 'COBRO',
        create_date = instance.start_date,
        commission_charged_to = instance.credit.client,
        )

pre_save.connect(repayment_amount_auto, sender= Credit)
post_save.connect(create_installments_auto, sender= Credit)

post_save.connect(up_installmet, sender=Installment)

#-------------------- SEÑALES PARA REFINANCIACION Y CUOTAS --------------------
def refinancing_repayment_amount_auto(instance, *args, **kwargs):

        refinancing = instance
        interests_amount = Decimal(float(refinancing.amount_refinancing) * (float(refinancing.refinancing_interest) / 100))
        repayment_amount = refinancing.amount_refinancing + interests_amount
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