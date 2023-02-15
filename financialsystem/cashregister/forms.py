from django import forms
from crispy_forms.helper import FormHelper
from django.forms import inlineformset_factory
from cashregister.models import CashRegister, Movement
from django.contrib.auth.models import User
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
    user = forms.ModelChoiceField(
        queryset= User.objects.all(),
        initial= 0,
        required= True,
        label= 'Caja',
    )
    
    class Meta:
        model = Movement
        fields = ["amount", "description", "money_type", "operation_mode", "cashregister", "user"]
        
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(MovementForm, self).__init__(*args, **kwargs)
        print(self.request.user.id)
        self.fields["user"].initial = self.request.user.id
        self.helper = FormHelper