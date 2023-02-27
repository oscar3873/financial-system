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
    
    prefix = 'guarantor'
    
    CIVIL_STATUS = (
        ('S','Soltero'),
        ('C', 'Casado'),
        ('V', 'Viudo'),
        ('D', 'Divorciado')
    )
    
    first_name = forms.CharField(
        label = 'Nombre/s',
    )
    
    last_name = forms.CharField(
        label = 'Apellido/s',
    )
    
    email = forms.EmailField(
        label= 'Correo Electrónico',
    )
    
    civil_status = forms.ChoiceField(
        choices= CIVIL_STATUS,
        label= "Estado Civil"
    )
    
    dni = forms.IntegerField(
        label= "DNI",
    )
    
    profession = forms.CharField(
        label= "Profesion",
    )
    
    address = forms.CharField(
        label= "Domicilio",
    )
    
    job_address = forms.CharField(
        label= "Domicilio Laboral",
    )
    
    class Meta:
        model = Guarantor
        fields = "__all__"
    
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        # print(kwargs)
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
        
        # Eliminar validación requerida
        for field in self.fields.values():
            field.required = False    
        
        self.helper = FormHelper
    #VALIDACION DEL DNI CAPTURA EL ERROR MOSTRANDO UN MENSAJE

#FORMULARIO PARA LA CREACION DE LOS NUMEROS DE TELEFONO
#------------------------------------------------------------------
class PhoneNumberForm(forms.ModelForm):
    
    prefix = 'guarantor'
    
    PhoneType = (
        ('C', 'Celular'), 
        ('F', 'Fijo'),
        ('A', 'Alternativo')
    )
    
    phone_number = forms.CharField(
        label = 'Telefono',
    )
    
    phone_type = forms.ChoiceField(
        choices= PhoneType,
        label="Tipo"
    )
    
    class Meta:
        model = PhoneNumber
        fields = "__all__"
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
        # Eliminar validación requerida
        for field in self.fields.values():
            field.required = False                

        self.helper = FormHelper

#------------------------------------------------------------------
PhoneNumberFormSet = inlineformset_factory(
    Guarantor, 
    PhoneNumber, 
    form = PhoneNumberForm,
    extra= 2,
    can_delete= True,
    can_delete_extra= True,
)