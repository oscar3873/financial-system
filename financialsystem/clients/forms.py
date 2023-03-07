from django import forms
from django.core.validators import validate_email
from django.forms import inlineformset_factory
from clients.models import Client, PhoneNumberClient
#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------
class ClientForm(forms.ModelForm):
    
    prefix = "client"
    
    CIVIL_STATUS = (
        ('S','Soltero'),
        ('C', 'Casado'),
        ('V', 'Viudo'),
        ('D', 'Divorciado')
    )
    
    SCORE = (
        (600 , 'Bueno (600)'),
        (400 , 'Regular (400)'),
        (200 , 'Riesgoso (200)')
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
        label= 'Correo',
        required=True,
    )
    civil_status = forms.ChoiceField(
        label="Estado Civil",
        choices= CIVIL_STATUS,
        required=True,
    )
    dni = forms.IntegerField(
        label= "DNI",
        required=True,
    )
    profession = forms.CharField(
        label= "Profesion",
        required=True,
    )
    address = forms.CharField(
        label= "Domicilio",
        required=True,
    )
    job_address = forms.CharField(
        label= "Domicilio Laboral",
        required=True,
    )
    
    class Meta:
        model = Client
        fields = "__all__"
        exclude = ["adviser"]

    def clean(self):
        cleaned_data = super().clean()
        fields_to_validate = ['first_name', 'last_name', 'address', 'job_address']
        
        for field_name in fields_to_validate:
            field_value = cleaned_data.get(field_name)
            if not field_value:
                self.add_error(field_name, 'Este campo es requerido')
                
        return cleaned_data
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if len(str(dni)) < 7 or  len(str(dni)) >= 15:
            raise forms.ValidationError("El DNI debe contener como minimo 7 y maximo 15 caracteres")

        # Verificar si ya existe un objeto con el mismo DNI en la base de datos
        if not self.instance.pk:
            if Client.objects.filter(dni=dni).exists():
                raise forms.ValidationError("Ya existe un Cliente con este DNI")

        return dni
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Validar formato de correo electrónico
        if not self.instance.pk:
            try:
                validate_email(email)
            except forms.ValidationError:
                raise forms.ValidationError("Ingrese un correo electrónico válido")

            # Verificar si ya existe un objeto con el mismo correo electrónico en la base de datos
            if Client.objects.filter(email=email).exists():
                raise forms.ValidationError("Ya existe un crédito asociado a este correo electrónico")

        return email

    def __init__(self, *args, **kwargs):
        self.is_update = kwargs.pop('is_update', False)
        super(ClientForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})

#FORMULARIO PARA LA CREACION DE LOS NUMEROS DE TELEFONO
#------------------------------------------------------------------
class PhoneNumberFormClient(forms.ModelForm):
    
    PhoneType = (
        ('C', 'Celular'), 
        ('F', 'Fijo'),
        ('A', 'Alternativo')
    )
    
    phone_number_c = forms.CharField(
        label = 'Telefono',
        required=False
    )
    
    phone_type_c = forms.ChoiceField(
        label="Tipo",
        choices= PhoneType,
        required=False,
    )

    class Meta:
        model = PhoneNumberClient
        fields = ('phone_number_c', 'phone_type_c')
    
    def clean_phone_number_c(self):
        phone_number_c = self.cleaned_data.get('phone_number_c')
        if phone_number_c is None or phone_number_c == '':
            return None
        elif not phone_number_c.isdigit():
            raise forms.ValidationError("El número de teléfono debe contener solo dígitos")
        elif len(phone_number_c) < 8 or len(phone_number_c) > 15:
            raise forms.ValidationError("El numero debe contener como minimo 8 y 15 digitos")
        return phone_number_c
    
    def __init__(self, *args, **kwargs):
        super(PhoneNumberFormClient,self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
        # Eliminar validación requerida
        for field in self.fields.values():
            field.required = False


#------------------------------------------------------------------
PhoneNumberFormSet = inlineformset_factory(
    Client, 
    PhoneNumberClient, 
    form = PhoneNumberFormClient,
    extra= 2,
    can_delete= False,
)

#FORMULARIO PARA LA CREACION DE CREDITOS
#------------------------------------------------------------------