from django import forms
from crispy_forms.helper import FormHelper
from django.forms import inlineformset_factory
from cashregister.models import CashRegister, Movement
#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------
class MovementForm(forms.ModelForm):
    
    MONEY_TYPE = (
        ('PESO', 'PESO'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRANSFER', 'TRANSFER'),
        ('CREDITO', 'CREDITO'),
        ('DEBITO', 'DEBITO'),
    )
    
    OPERATION_CHOISE = (
        ('Ingreso', 'Ingreso'),
        ('Egreso', 'Egreso')
    )
    
    amount = forms.DecimalField(
        label = 'Monto',
        required=True,
    )
    description = forms.CharField(
        widget=forms.Textarea,
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
    cashregister = forms.ModelChoiceField(
        queryset= CashRegister.objects.all(),
        initial= 0,
        required= True,
        label= 'Caja',
    )
    
    class Meta:
        model = Movement
        fields = ["amount", "description", "money_type", "operation_mode", "cashregister"]
        
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper