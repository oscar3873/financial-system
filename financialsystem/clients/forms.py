from django import forms
from crispy_forms.helper import FormHelper
from django.forms import inlineformset_factory
from clients.models import Client, PhoneNumber
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
        
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper
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