from datetime import datetime
from django import forms
from crispy_forms.helper import FormHelper
from .models import Credit
from clients.models import Client
from django.forms import NumberInput

#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------
class CreditForm(forms.ModelForm):
    
    credit_interest = forms.IntegerField(
        label= "Intereses",
        required= True,
        initial= 40,
        min_value= 0,
        max_value= 100    
    )
    
    amount = forms.DecimalField(
        label= "Monto Solicitado",
        required= True,
    )
    
    installment_num = forms.IntegerField(
        label= "Numero de Cuotas",
        required= True,
        min_value=1,
        max_value=12,
    )
    
    start_date = forms.DateField(
        label="Fecha de Entrada",
        widget=  NumberInput(attrs={
            'type': 'date',
            'value': datetime.now().date()
            })
    )
    
    end_date = forms.DateField(
        label="Fecha de Vto.",
        widget=  NumberInput(attrs={
            'type': 'date',
            })
    )
    
    
    class Meta:
        model = Credit
        fields = ["amount", "credit_interest", "installment_num", "start_date", "end_date"]
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        super(CreditForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper