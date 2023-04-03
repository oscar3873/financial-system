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
        widget=forms.NumberInput(
            attrs={'id': 'id_amount_form'}
            ),
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={'id': 'id_description_form'}
            ),
        label = 'Descripcion de la operacion',
        required=True,
    )
    money_type = forms.ChoiceField(
        choices = MONEY_TYPE,
        label= 'Seleccione divisa',
        required=True,
        widget=forms.Select(
            attrs={'id': 'id_money_type_form'}
            ),
    )
    operation_mode = forms.ChoiceField(
        choices= OPERATION_CHOISE,
        label= 'Seleccione operacion',
        required=True,
        widget=forms.Select(
            attrs={'id': 'id_operation_mode_form'}
            ),
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

class CashregisterFormPassword(forms.ModelForm):
    auth_expenses = forms.CharField(
        label="Cambiar contraseña de caja (EGRESO)",
        min_length=1,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-2', 'placeholder': 'Contraseña actual: %s'%CashRegister.objects.first().auth_expenses}
        )
    )
    class Meta:
        model = CashRegister
        fields = ['auth_expenses']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['auth_expenses'].initial = CashRegister.objects.first()