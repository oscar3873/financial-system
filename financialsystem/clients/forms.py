from datetime import date
from django import forms
from crispy_forms.helper import FormHelper
from django.forms import inlineformset_factory
from clients.models import Client, PhoneNumber
from django.contrib.auth.models import User
from credit.models import Credit
#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------
class ClientForm(forms.ModelForm):
    
    CivilStatus = (
        ('S','Soltero'),
        ('C', 'Casado'),
        ('V', 'Viudo'),
        ('D', 'Divorciado')
    )
    
    first_name = forms.CharField(
        label = 'Nombre/s',
        required=True,
    )
    last_name = forms.CharField(
        label = 'Apellido/s',
        required=True,
    )
    email = forms.EmailField(
        label= 'Correo Electrónico',
        required=True,
    )
    civil_status = forms.ChoiceField(
        choices= CivilStatus,
        required=True,
    )
    dni = forms.IntegerField(
        label= "DNI",
        required= True,
    )
    profession = forms.CharField(
        label= "Profesion",
        required= True,
    )
    address = forms.CharField(
        label= "Domicilio",
        required= True,
    )
    job_address = forms.CharField(
        label= "Domicilio Laboral",
        required= True,
    )
    
    
    class Meta:
        model = Client
        fields = "__all__"
        exclude = ["adviser"]
        
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        # request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper
        # self.fields['user'].initial = request.user.id
    #VALIDACION DEL DNI CAPTURA EL ERROR MOSTRANDO UN MENSAJE

#FORMULARIO PARA LA CREACION DE LOS NUMEROS DE TELEFONO
#------------------------------------------------------------------
class PhoneNumberForm(forms.ModelForm):
    
    PhoneType = (
        ('C', 'Celular'), 
        ('F', 'Fijo'),
        ('A', 'Alternativo')
    )
    
    phone_number = forms.CharField(
        label = 'Nombre/s',
        required=True,
    )
    
    phone_type = forms.ChoiceField(
        choices= PhoneType,
        required=True,
    )
    
    class Meta:
        model = PhoneNumber
        fields = "__all__"
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        print(kwargs)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper

#------------------------------------------------------------------
PhoneNumberFormSet = inlineformset_factory(
    Client, 
    PhoneNumber, 
    form = PhoneNumberForm,
    extra= 0,
    can_delete= True,
    can_delete_extra= True,
)

#FORMULARIO PARA LA CREACION DE CREDITOS
#------------------------------------------------------------------
class CreditForm(forms.ModelForm):

    amount = forms.DecimalField(
        label= 'Monto',
        required=True,
    )

    installment_num = forms.IntegerField(
        label='Cuotas',
        required=True,
        max_value=12,
        min_value=1
    )

    credit_interest = forms.IntegerField(
        label='Interes',
        required=True,
    )

    start_date = forms.DateField(
        label='Fecha de Inicio',
        required=True,
        widget=forms.DateTimeInput(
            attrs={'type': 'date', 'value': '%s' % date.today()}
        )
    )
    
    class Meta:
        model = Credit
        fields = ('amount', 'installment_num','credit_interest', 'start_date')

    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper


#------------------------------------------------------------------
CreditFormSet = inlineformset_factory(
    Client,
    Credit,
    form = CreditForm,
    extra= 1,
    can_delete=True,
    can_delete_extra= True,
    )

#----------------------------------------------------------------
class PaymentForm(forms.Form):
    MONEY_TYPE = [
        ('PESOS','PESOS'),
        ('USD','USD'),
        ('EUR', 'EUR'),
        ('TRANSFER','TRANSFERENCIA'),
        ]
    
    operation_mode = forms.ChoiceField(
        choices= MONEY_TYPE,
        required=True,
        label='Medio de Pago',
    )

    def __init__(self, object, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper
        excludes = ['Refinanciada', 'Pagada']
        installments = object.client_credits.last().installment.exclude(condition__in=excludes)
        if installments.count() > 0:
            for installment in installments:
                if installment == installments.first():
                    self.fields['Cuota %s' %str(installment.installment_number)] = forms.BooleanField(label='Cuota %s' % (installment.installment_number),required=True)
                else:
                    self.fields['Cuota %s' %str(installment.installment_number)] = forms.BooleanField(label='Cuota %s' % (installment.installment_number),required=False)
