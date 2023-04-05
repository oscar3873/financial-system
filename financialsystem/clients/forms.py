from django import forms
from django.core.validators import validate_email
from django.forms import inlineformset_factory
from clients.models import Client, PhoneNumberClient
#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------

class ClientForm(forms.ModelForm):
    
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
        required=False,
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
        required=False,
    )
    address = forms.CharField(
        label= "Domicilio",
        required=False,
    )
    job_address = forms.CharField(
        label= "Domicilio Laboral",
        required=False,
    )
    

    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'civil_status', 'dni', 'profession', 'address', 'score', 'job_address']


    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) < 3:
            raise forms.ValidationError("El nombre debe contener al menos 3 caracteres")
        return str(first_name).upper()
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) < 3:
            raise forms.ValidationError("El apellido debe contener al menos 3 caracteres")
        return str(last_name).upper()

    def clean_dni(self):
        """
        Validar que el DNI sea válido
        """
        dni = self.cleaned_data.get('dni')
        if len(str(dni)) < 7 or  len(str(dni)) >= 15:
            raise forms.ValidationError("El DNI debe contener como minimo 7 y maximo 15 caracteres")

        if Client.objects.filter(dni=dni).exists():
            if Client.objects.filter(dni=dni).first() != self.instance:
                raise forms.ValidationError("Ya existe un Cliente con DNI {}".format(dni))
        return dni
    
    def clean_email(self):
        """
        Validar que el correo electrónico sea válido
        """
        email = self.cleaned_data.get('email')
        if len(email) > 0:
            try:
                validate_email(email)
            except forms.ValidationError:
                raise forms.ValidationError("Ingrese un correo electrónico válido")
        
            if Client.objects.filter(email=email).exists():
                if Client.objects.filter(email=email).first() != self.instance:
                    raise forms.ValidationError("Ya existe un crédito asociado a este correo electrónico") 
        return email

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
            
        if kwargs.get('prefix') == 'guarantor': # CLIENTES PUEDEN SER TAMBIEN GARANTES DE OTROS CLIENTES
            for field in self.fields.values():
                field.required = False


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
        required=False,
        widget=forms.NumberInput(
        attrs={'type':'number'}
        )
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
        """
        Validar que el número de teléfono sea válido
        """	
        phone_number_c = self.cleaned_data.get('phone_number_c')
        if phone_number_c is None or phone_number_c == '':
            return None
        elif not phone_number_c.isdigit():
            raise forms.ValidationError("El número de teléfono debe contener solo dígitos")
        elif len(phone_number_c) < 8 or len(phone_number_c) > 20:
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
    extra= 3,
    can_delete= False,
)
PhoneNumberFormSetUpdate = inlineformset_factory(
    Client, 
    PhoneNumberClient, 
    form = PhoneNumberFormClient,
    extra= 0,
    can_delete= False,
)
