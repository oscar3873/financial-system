from django import forms
from crispy_forms.helper import FormHelper
from cashregister.models import CashRegister, Movement
from adviser.models import Adviser
#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------
class MovementForm(forms.ModelForm):
    
    MONEY_TYPE = (
        ('PESOS', 'PESOS'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRANSFER', 'TRANSFER'),
        ('CREDITO', 'CREDITO'),
        ('DEBITO', 'DEBITO'),
    )
    
    OPERATION_CHOISE = (
        ('INGRESO', 'INGRESO'),
        ('EGRESO', 'EGRESO')
    )
    
    amount = forms.DecimalField(
        label = 'Monto',
        required=True,
    )
    description = forms.CharField(
        widget=forms.Textarea(),
        label = 'Descripcion de la operacion',
        required=True,
    )
    money_type = forms.ChoiceField(
        choices = MONEY_TYPE,
        label= 'Seleccione divisa',
        required=True,
    )
    operation_mode = forms.ChoiceField(
        choices= OPERATION_CHOISE,
        label= 'Seleccione el tipo de operacion',
        required=True,
    )
    
    class Meta:
        model = Movement
        fields = ["amount", "description", "money_type", "operation_mode"]
        
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(MovementForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['operation_mode'].widget = forms.HiddenInput()
        
class MovementUpdateForm(forms.ModelForm):
    
    MONEY_TYPE = (
        ('PESOS', 'PESOS'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRANSFER', 'TRANSFER'),
        ('CREDITO', 'CREDITO'),
        ('DEBITO', 'DEBITO'),
    )
    
    OPERATION_CHOISE = (
        ('INGRESO', 'INGRESO'),
        ('EGRESO', 'EGRESO')
    )
    
    amount = forms.DecimalField(
        label = 'Monto',
        required=True,
    )
    description = forms.CharField(
        widget=forms.Textarea(),
        label = 'Descripcion de la operacion',
        required=True,
    )
    money_type = forms.ChoiceField(
        choices = MONEY_TYPE,
        label= 'Seleccione divisa',
        required=True,
    )
    operation_mode = forms.ChoiceField(
        choices= OPERATION_CHOISE,
        label= 'Seleccione el tipo de operacion',
        required=True,
    )
    
    class Meta:
        model = Movement
        fields = ["amount", "description", "money_type", "operation_mode"]
        
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(MovementUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})