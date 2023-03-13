from decimal import Decimal
import uuid
from django.db import models
from clients.models import Client
from cashregister.models import Movement
from django.db.models.signals import post_save, pre_save, pre_delete
from datetime import datetime, timedelta
# Create your models here.
#CREDITO

class Credit(models.Model):
    CHOICE = [
        ('Pagado', 'Pagado'),
        ('A Tiempo','A Tiempo'),
        ('Vencido', 'Vencido'),
        ]

    is_active = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False, help_text="El credito esta pagado")
    is_old_credit = models.BooleanField(default=False, help_text="Es un credito antiguo")
    is_new = models.BooleanField(default=False, help_text="Se han modificados algunos campos") # PARA REALIZAR UN UPDATE BASADO EN CAMBIOS DE CAMPOS

    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    condition = models.CharField(max_length=15,choices=CHOICE, default='A Tiempo')
    credit_interest = models.PositiveIntegerField(default=40, help_text="Intereses de credito")
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto del Credito")
    mov = models.OneToOneField(Movement,on_delete=models.SET_NULL,null=True,blank=True)
    credit_repayment_amount = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=15, help_text="Monto de Devolucion del Credito")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True, default=None, help_text="Cliente del Credito", related_name="credits")
    installment_num = models.PositiveIntegerField(default=1, null=True, help_text="Numeros de Cuotas")
    start_date = models.DateTimeField(verbose_name='Fecha de Inicio',default=datetime.now, null=True)
    end_date = models.DateTimeField(verbose_name='Fecha de Finalizacion del Credito', null=True)
    payment_date = models.DateTimeField(verbose_name="Fecha de Pago",blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        
        if self.client:
            return "Credito de {}, {}".format(self.client.first_name, self.client.last_name)
        else:
            return super().__str__()
        
    class Meta:
        ordering = ["-created_at"]
            

#REFINANCIACION   
class Refinancing(models.Model):
    
    is_paid = models.BooleanField(default=False, help_text="La refinanciacion esta pagada")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interest = models.PositiveIntegerField(default=48, help_text="Intereses de la refinanciacion")
    amount = models.DecimalField(decimal_places=2, max_digits=15)
    refinancing_repayment_amount = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=15, help_text="Monto de Devolver de la Refinanciacion")
    installment_num_refinancing = models.PositiveIntegerField(default=1, null=True, help_text="Numeros de Cuotas")
    payment_date = models.DateTimeField(help_text="Fecha de Pago", null=True, blank=True)
    lastup = models.DateField(null=True, blank=True) #PARA CALCULO DE INTERESES DIARIOS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        installment_numbers = [str(installment.installment_number) for installment in self.installment_ref.all()]
        return "Refinanciacion de las cuotas: {}".format(", ".join(installment_numbers))

    class Meta:
        ordering = ["-created_at"]

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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    refinance = models.ForeignKey(Refinancing,on_delete=models.SET_NULL, null=True, blank=True, related_name='installment_ref')
    installment_number = models.PositiveSmallIntegerField(help_text="Numero de cuota del credito")
    daily_interests = models.DecimalField(blank=False, decimal_places=2, max_digits=20, null=True, default=0, help_text="Intereses diarios")
    start_date = models.DateTimeField(default=datetime.now, null=True)
    end_date = models.DateTimeField(null=True)
    payment_date = models.DateTimeField(help_text="Fecha de Pago", null=True, blank=True)
    condition = models.CharField(max_length=15,choices=CONDITION, default='A Tiempo')
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name="installments", help_text="Credito de la cuota")
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto de la cuota")
    lastup = models.DateField(null=True) #PARA CALCULO DE INTERESES DIARIOS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return "Cuota {} del {}".format(self.installment_number, self.credit)

    class Meta:
        ordering = ['created_at']
        
#CUOTA DE REFINANCIACION
class InstallmentRefinancing(models.Model):
    CHOICE = [
        ('Pagada', 'Pagada'),
        ('A Tiempo','A Tiempo'),
        ]

    is_caduced_installment = models.BooleanField(default=False , help_text="La cuota esta vencida")
    is_paid_installment = models.BooleanField(default=False, help_text="La cuota esta pagada")
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    condition = models.CharField(max_length=15,choices=CHOICE, default='A Tiempo')
    installment_number = models.PositiveSmallIntegerField(help_text="Numero de cuota de la refinanciacion")
    daily_interests = models.DecimalField(blank=False, decimal_places=2, max_digits=20, null=True, default=0, help_text="Intereses diarios")
    refinancing = models.ForeignKey(Refinancing, on_delete=models.CASCADE, related_name="installments", help_text="Refinanciacion de la cuota")
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto de la cuota de refinanciacion")
    payment_date = models.DateTimeField(verbose_name="Fecha de Pago",blank=True, null=True)
    start_date = models.DateTimeField(default=datetime.now, verbose_name='Fecha de Inicio')
    end_date = models.DateTimeField(verbose_name='Fecha de Vencimiento',blank=True, null=True)
    lastup = models.DateField(null=True) #PARA CALCULO DE INTERESES DIARIOS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return "Cuota {} de la {}".format(self.installment_number, self.refinancing)
    
    class Meta:
        ordering = ["created_at"]

#-------------------- SEÑALES PARA CREDITOS Y CUOTAS --------------------
def repayment_amount_auto(instance, *args, **kwargs):
    """
    Calcula el monto de devolver del Credito.
    Ademas, sirve para cuando el credito recive una modificacion de algun campo, exceptuando
    el campo 'is_new', el cual nos da la pauta si el credito fue modificado (se uso un Credit.save() por update)
    Ej. update: 'credit.amount = <new_amount>' -> credit.save() -> repayment_amount_auto() -> news installments
    """
    credit = instance
    
    if credit.is_new:
        credit.end_date = (timedelta(days=30)*credit.installment_num) + credit.start_date
        repayment_amount = credit.installment_num*(Decimal(credit.credit_interest/100)*credit.amount)/(1-pow((1+Decimal(credit.credit_interest/100)),(- credit.installment_num)))
        credit.credit_repayment_amount = Decimal(repayment_amount)
        
    credit.is_active = True

    if instance.is_paid:
        instance.is_active = False
        instance.condition = 'Pagado'


def create_installments_auto(instance, created, *args, **kwargs):
    """
    Crea las cuotas del credito.
    Borra las cuotas aderidas en caso de actualizacion de campos sencibles:
            ('amount', 'installment_num', 'credit_interest')
    """
    if instance.is_new or created:
        instance.installments.all().delete() # Actualizacion de credito (crea nuevas cuotas en base los nuevos datos del credito, borrando las cuotas anteriores)
        credit = instance
        days = 30
        amount_installment = Decimal(credit.credit_repayment_amount/credit.installment_num)
        for numberInstallments in range(credit.installment_num):
            end_date = credit.start_date + timedelta(days=days)
            numberInstms = numberInstallments + 1
            credit.installments.create(
                installment_number=numberInstms, 
                start_date = credit.start_date,
                credit= credit, 
                amount= amount_installment, 
                end_date=end_date,
                lastup=end_date
                )
            days += 30
    if instance.is_new:
        instance.is_new = False
        instance.save()


def update_installment(instance, *args, **kwargs):
    if instance.condition == 'Pagada':
        instance.is_paid_installment = True
    elif instance.condition == 'Vencida':
        instance.is_caduced_installment = True
    elif instance.condition == 'Refinanciada':
        instance.is_refinancing_installment = True
    else:
        instance.is_refinancing_installment = False
        instance.is_paid_installment = False
        instance.is_caduced_installment = False

def delete_installment(instance, *args, **kwargs):
    if instance.refinance: 
        instance.refinance.delete()


pre_save.connect(repayment_amount_auto, sender= Credit)
pre_save.connect(update_installment, sender=Installment)
pre_save.connect(update_installment, sender=InstallmentRefinancing)

post_save.connect(create_installments_auto, sender= Credit)

pre_delete.connect(delete_installment, sender=Installment)

#-------------------- SEÑALES PARA REFINANCIACION Y CUOTAS --------------------
def refinancing_repayment_amount_auto(instance, *args, **kwargs):
    """
    Calcula el monto de devolver de la Refinanciacion.
    """
    refinancing = instance

    match (int(refinancing.installment_num_refinancing)):
        case 3: refinancing.interest = 25
        case 6: refinancing.interest = 50
        case 9: refinancing.interest = 75
        case _: refinancing.interest = 100

    
    repayment_amount = refinancing.amount
    refinancing.refinancing_repayment_amount = Decimal(repayment_amount)
    refinancing.amount = Decimal(refinancing.amount / Decimal(1 + float(refinancing.interest) / 100))
    refinancing.end_date = datetime.now() + timedelta(days=30)*refinancing.installment_num_refinancing


def create_installmentsR_auto(instance, created, *args, **kwargs):
    """
    Crea cuotas de Refinanciacion.
    """
    if created:
        refinancing = instance
        days = 30
        amount_installment = Decimal(refinancing.refinancing_repayment_amount/refinancing.installment_num_refinancing)
        for numberInstallments in range(refinancing.installment_num_refinancing):
            end_date = instance.created_at + timedelta(days=days)
            numberInstms = numberInstallments + 1
            refinancing.installments.create(installment_number=numberInstms, refinancing=refinancing, amount=amount_installment, end_date=end_date, lastup=end_date)
            days += 30


pre_save.connect(refinancing_repayment_amount_auto, sender=Refinancing)
post_save.connect(create_installmentsR_auto, sender=Refinancing)