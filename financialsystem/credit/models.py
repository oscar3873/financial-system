import uuid
from decimal import Decimal
from django.db import models
from clients.models import Client
from cashregister.models import Movement
from django.db.models.signals import post_save, pre_save, pre_delete
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone


from core.utils import round_to_nearest_hundred
from guarantor.models import Guarantor
from adviser.models import Adviser
# Create your models here.
#CREDITO

date = timezone.now

class Credit(models.Model):
    CHOICE = [
        ('Pagado', 'Pagado'),
        ('A Tiempo','A Tiempo'),
        ('Vencido', 'Vencido'),
        ]

    is_active = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False, help_text="El credito esta pagado")
    is_old_credit = models.BooleanField(default=False, help_text="Es un credito antiguo")
    has_pay_stub = models.BooleanField(blank=True, default=False, verbose_name="Recibo de sueldo")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    condition = models.CharField(max_length=15,choices=CHOICE, default='A Tiempo')
    interest = models.DecimalField(decimal_places=2, max_digits=15,default=40, help_text="Intereses de credito")
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto del Credito")
    mov = models.OneToOneField(Movement,on_delete=models.SET_NULL,null=True,blank=True)
    adviser = models.ForeignKey(Adviser, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    credit_repayment_amount = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=15, help_text="Monto de Devolucion del Credito")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True, default=None, help_text="Cliente del Credito", related_name="credits")
    guarantor = models.ForeignKey(Guarantor, on_delete=models.SET_NULL, blank=True, null=True, default=None, help_text="Cliente del Credito", related_name="credits_g")
    installment_num = models.PositiveIntegerField(default=1, null=True, help_text="Numeros de Cuotas")
    start_date = models.DateTimeField(verbose_name='Fecha de Inicio',default=date, null=True)
    end_date = models.DateTimeField(verbose_name='Fecha de Finalizacion del Credito', null=True)
    payment_date = models.DateTimeField(verbose_name="Fecha de Pago",blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        
        if self.client:
            return "Credito de {}, {}".format(self.client.last_name, self.client.first_name)
        else:
            return super().__str__()
        
    def detail_str(self):
        if self.client:
            return "Credito de {} {} | Monto ${} | Cuotas: {} | Fecha de alta: {}".format(self.client.first_name, self.client.last_name, self.amount, self.installment_num, self.created_at.date().strftime('%d/%m/%Y'))
        else:
            return self.__str__()
        
    class Meta:
        ordering = ["-created_at"]
            

#REFINANCIACION   
class Refinancing(models.Model):
    is_new = models.BooleanField(default=False, help_text="La refinanciacion es nueva o actualizada")
    is_paid = models.BooleanField(default=False, help_text="La refinanciacion esta pagada")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interest = models.PositiveIntegerField(default=48, help_text="Intereses de la refinanciacion")
    amount = models.DecimalField(decimal_places=2, max_digits=15)
    refinancing_repayment_amount = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=15, help_text="Monto de Devolver de la Refinanciacion")
    installment_num = models.PositiveIntegerField(default=1, null=True, help_text="Numeros de Cuotas")
    payment_date = models.DateTimeField(help_text="Fecha de Pago", null=True, blank=True)
    # lastup = models.DateField(null=True, blank=True) #PARA CALCULO DE INTERESES DIARIOS
    end_date = models.DateTimeField(verbose_name='Fecha de Finalizacion de Refinanciacion', null=True)
    start_date = models.DateTimeField(default=date, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name="refinancing", help_text="Credito de la cuota", null=True, blank=True)
    
    def __str__(self) -> str:
        installment_numbers = [str(installment.installment_number) for installment in self.installment_ref.all()]
        return "Refinanciacion de la cuota: {} de {}".format(", ".join(installment_numbers), self.credit)

    def resumen_str_(self) -> str:
        installment_numbers = [str(installment.installment_number) for installment in self.installment_ref.all()]
        return "Refinanciacion de la cuota: {}".format(", ".join(installment_numbers))

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
    porcentage_daily_interests = models.DecimalField(blank=False, decimal_places=2, max_digits=20, null=True, default=2, help_text="Intereses diarios")
    start_date = models.DateTimeField(default=date, null=True)
    end_date = models.DateTimeField(null=True, default=None)
    payment_date = models.DateTimeField(help_text="Fecha de Pago", null=True, blank=True)
    condition = models.CharField(max_length=15,choices=CONDITION, default='A Tiempo')
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name="installments", help_text="Credito de la cuota")
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto de la cuota+Intereses")
    original_amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto de la cuota")
    lastup = models.DateField(null=True) #PARA CALCULO DE INTERESES DIARIOS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return "Cuota {} del {}".format(self.installment_number, self.credit)

    class Meta:
        ordering = ['created_at']
        
#CUOTA DE REFINANCIACION
class InstallmentRefinancing(models.Model):
    CONDITION = [
        ('Pagada', 'Pagada'),
        ('Vencida','Vencida'),
        ('A Tiempo','A Tiempo')
        ]

    is_caduced_installment = models.BooleanField(default=False , help_text="La cuota esta vencida")
    is_paid_installment = models.BooleanField(default=False, help_text="La cuota esta pagada")
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    condition = models.CharField(max_length=15,choices=CONDITION, default='A Tiempo')
    installment_number = models.PositiveSmallIntegerField(help_text="Numero de cuota de la refinanciacion")
    daily_interests = models.DecimalField(blank=False, decimal_places=2, max_digits=20, null=True, default=0, help_text="Intereses diarios")
    porcentage_daily_interests = models.DecimalField(blank=False, decimal_places=2, max_digits=20, null=True, default=2, help_text="Intereses diarios")
    refinancing = models.ForeignKey(Refinancing, on_delete=models.CASCADE, related_name="installments", help_text="Refinanciacion de la cuota")
    amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto de la cuota de refinanciacion")
    original_amount = models.DecimalField(decimal_places=2, max_digits=15, help_text="Monto de la cuota")
    payment_date = models.DateTimeField(verbose_name="Fecha de Pago",blank=True, null=True)
    start_date = models.DateTimeField(default=date, verbose_name='Fecha de Inicio')
    end_date = models.DateTimeField(verbose_name='Fecha de Vencimiento',blank=True, null=True, default=None)
    lastup = models.DateField(null=True) #PARA CALCULO DE INTERESES DIARIOS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name="installments_refinancing", help_text="Credito de la cuota", null=True, blank=True)
    
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
    

    if not credit.is_old_credit:
        credit.end_date = (timedelta(days=30)*credit.installment_num) + credit.start_date
        credit.amount = round_to_nearest_hundred(credit.amount)
        installment_value = round_to_nearest_hundred((Decimal(credit.interest/100)*credit.amount)/(1-pow((1+Decimal(credit.interest/100)),(- credit.installment_num))))
        repayment_amount = credit.installment_num*installment_value
        credit.credit_repayment_amount = round_to_nearest_hundred(repayment_amount)
        credit.is_paid = False
        instance.condition = 'A Tiempo'
        
    credit.is_active = True

    if instance.is_paid:
        instance.is_active = False
        instance.condition = 'Pagado'

    
def create_installments_auto(instance, created, *args, **kwargs):
    """
    Crea las cuotas del credito.
    Borra las cuotas aderidas en caso de actualizacion de campos sencibles:
            ('amount', 'installment_num', 'interest')
    """
    if not instance.is_old_credit or created:
        instance.installments.all().delete() # Actualizacion de credito (crea nuevas cuotas en base los nuevos datos del credito, borrando las cuotas anteriores)
        try:
            for installment_with_ref in instance.installments.filter(refinance__isnull=False):
                installment_with_ref.refiannce.delete()
        except: pass
        credit = instance
        amount_installment = Decimal(credit.credit_repayment_amount/credit.installment_num)

        start_date = credit.start_date
        for numberInstallments in range(credit.installment_num):
            end_date = start_date + relativedelta(months=+1)
            numberInstms = numberInstallments + 1
            
            credit.installments.create(
                installment_number=numberInstms, 
                start_date = start_date,
                credit= credit, 
                amount= amount_installment,
                original_amount = amount_installment,
                end_date=end_date,
                lastup=end_date
                )
            start_date = end_date

    if not instance.is_old_credit:
        instance.is_old_credit = True
        instance.save()


def update_installment(instance, *args, **kwargs):
    if instance.condition == 'Pagada':
        instance.is_paid_installment = True
    elif instance.condition == 'Vencida':
        instance.is_caduced_installment = True
        instance.is_paid_installment = False
    elif instance.condition == 'Refinanciada':
        instance.is_refinancing_installment = True
        instance.is_caduced_installment = False
    else:
        instance.is_refinancing_installment = False
        instance.is_paid_installment = False
        instance.is_caduced_installment = False    


def delete_installment(instance, *args, **kwargs):
    try: 
        instance.refinance.delete()
    except:
        pass

def delete_credit(instance, *args, **kwargs):
    try:
        if instance.mov:
            instance.mov.delete()
    except:
        pass


pre_save.connect(repayment_amount_auto, sender= Credit)
pre_save.connect(update_installment, sender=Installment)
pre_save.connect(update_installment, sender=InstallmentRefinancing)

post_save.connect(create_installments_auto, sender= Credit)

pre_delete.connect(delete_installment, sender=Installment)
pre_delete.connect(delete_credit, sender=Credit)

#-------------------- SEÑALES PARA REFINANCIACION Y CUOTAS --------------------
def refinancing_repayment_amount_auto(instance, *args, **kwargs):
    """
    Calcula el monto de devolver de la Refinanciacion.
    """
    refinancing = instance

    if refinancing.is_new:
        match (int(refinancing.installment_num)):
            case 3: refinancing.interest = 25
            case 6: refinancing.interest = 50
            case 9: refinancing.interest = 75
            case _: refinancing.interest = 100

        refinancing.refinancing_repayment_amount = refinancing.amount
        refinancing.amount = round_to_nearest_hundred(refinancing.amount / Decimal(1 + float(refinancing.interest) / 100))
        refinancing.end_date = refinancing.start_date + relativedelta(months=int(refinancing.installment_num))

    refinancing.is_new = False

def create_installmentsR_auto(instance, created, *args, **kwargs):
    """
    Crea cuotas de Refinanciacion.
    """
    if created:
        refinancing = instance
        amount_installment = Decimal(refinancing.refinancing_repayment_amount/refinancing.installment_num)

        start_date = instance.start_date
        for numberInstallments in range(refinancing.installment_num):
            end_date = start_date + relativedelta(months=+1)
            numberInstms = numberInstallments + 1
            
            refinancing.installments.create(
                installment_number=numberInstms, 
                start_date = start_date,
                credit= refinancing.credit, 
                amount= amount_installment,
                original_amount=amount_installment,
                end_date=end_date,
                lastup=end_date
                )
            start_date = end_date

def installment_reset_refinance(instance, *args, **kwargs):
    try:
        for installment in instance.installment_ref.all():
            installment.condition = 'A Tiempo'
            installment.save()
    except: pass

pre_save.connect(refinancing_repayment_amount_auto, sender=Refinancing)
post_save.connect(create_installmentsR_auto, sender=Refinancing)

pre_delete.connect(installment_reset_refinance, sender=Refinancing)