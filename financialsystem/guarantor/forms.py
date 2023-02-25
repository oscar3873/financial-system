from datetime import date, datetime
from django import forms
from crispy_forms.helper import FormHelper
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from guarantor.models import Guarantor, PhoneNumber
from clients.models import Client
#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------
class GuarantorForm(forms.ModelForm):
    
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
    
    client = forms.ModelChoiceField(
        queryset= Client.objects.all(),
        initial= Client.objects.last(),
        required= True,
        label= "Cliente"
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
        label= "Estado Civil"
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
        model = Guarantor
        fields = "__all__"
    
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        # print(kwargs)
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
    Guarantor, 
    PhoneNumber, 
    form = PhoneNumberForm,
    extra= 0,
    can_delete= True,
    can_delete_extra= True,
)