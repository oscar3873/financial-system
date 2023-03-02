from django import forms
from crispy_forms.helper import FormHelper
from django.forms import inlineformset_factory
from guarantor.models import Guarantor, PhoneNumberGuarantor

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
class PhoneNumberFormGuarantor(forms.ModelForm):
    
    PhoneType = (
        ('C', 'Celular'), 
        ('F', 'Fijo'),
        ('A', 'Alternativo')
    )
    
    phone_number_g = forms.CharField(
        label = 'Telefono',
    )
    
    phone_type_g = forms.ChoiceField(
        choices= PhoneType,
        label="Tipo"
    )
    
    class Meta:
        model = PhoneNumberGuarantor
        fields = ('phone_number_g', 'phone_type_g')
    
    def clean_phone_number_g(self):
        phone_number_g = self.cleaned_data.get('phone_number_g')
        if phone_number_g is None or phone_number_g == '':
            return None
        elif not phone_number_g.isdigit():
            raise forms.ValidationError("El número de teléfono debe contener solo dígitos")
        elif len(phone_number_g) < 8 or len(phone_number_g) > 15:
            raise forms.ValidationError("El numero debe contener como minimo 8 y 15 digitos")
        return phone_number_g    
    
    def __init__(self, *args, **kwargs):
        super(PhoneNumberFormGuarantor,self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
        # Eliminar validación requerida
        for field in self.fields.values():
            field.required = False                
        self.prefix = "guarantor"
        self.helper = FormHelper

#------------------------------------------------------------------
PhoneNumberFormSetG = inlineformset_factory(
    Guarantor, 
    PhoneNumberGuarantor, 
    form = PhoneNumberFormGuarantor,
    extra= 2,
    can_delete= False,
)