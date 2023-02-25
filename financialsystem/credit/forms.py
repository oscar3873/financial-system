from datetime import datetime
from django import forms
from crispy_forms.helper import FormHelper
from .models import Credit
from clients.models import Client
from django.forms import NumberInput

#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------
class CreditForm(forms.ModelForm):
    
    is_paid_credit = forms.BooleanField(
        label = "Esta pagado?",
        required= False,
    )
    
    is_old_credit = forms.BooleanField(
        label= "Es un Credito antiguo?",
        required= False,
    )
    
    credit_interest = forms.IntegerField(
        label= "Intereses del Credito",
        required= True,    
    )
    
    amount = forms.DecimalField(
        label= "Monto Solicitado",
        required= True,
    )
    
    client = forms.ModelChoiceField(
        label= "Seleccione Cliente",
        queryset= Client.objects.all(),
        initial= 1,
        required= True,
    )
    
    installment_num = forms.IntegerField(
        label= "Numero de Cuotas",
        required= True,
    )
    
    created = forms.DateField(
        label="Ingresar fecha del Credito",
        widget=  NumberInput(attrs={
            'type': 'date',
            'value': datetime.now().date()
            })
    )
    
    class Meta:
        model = Credit
        fields = ["amount", "credit_interest", "installment_num", "client", "is_old_credit", "created", "is_paid_credit"]
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        super(CreditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper