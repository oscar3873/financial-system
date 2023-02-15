from django import forms
from crispy_forms.helper import FormHelper
from .models import Credit
from clients.models import Client

#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------
class CreditForm(forms.ModelForm):
    
    is_paid_credit = forms.BooleanField(
        label = 'Esta pagado?',
        required= True,
    )
    
    credit_interest = forms.IntegerField(
        label='Intereses del Credito',
        required= True,    
    )
    
    amount = forms.DecimalField(
        label='Monto del Credito',
        required= True,
    )
    
    client = forms.ModelChoiceField(
        label="Seleccione Cliente",
        queryset= Client.objects.all(),
        initial= 1,
        required= True,
    )
    
    number_installment = forms.IntegerField(
        label="Numero de Cuotas",
        required= True,
    )
    
    class Meta:
        model = Credit
        fields = ["is_paid_credit", "credit_interest", "amount", "client", "number_installment"]
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        super(CreditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper