from django import forms
from django.core.validators import validate_email
from django.forms import inlineformset_factory
from clients.models import Client
from guarantor.models import Guarantor, PhoneNumberGuarantor

#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------
class GuarantorForm(forms.ModelForm):
        
    CIVIL_STATUS = (
        ('Soltero','Soltero'),
        ('Casado', 'Casado'),
        ('Viudo', 'Viudo'),
        ('Divorciado', 'Divorciado')
    )
    
    first_name = forms.CharField(
        label = 'Nombre/s',
    )
    
    last_name = forms.CharField(
        label = 'Apellido/s',
    )
    
    email = forms.EmailField(
        label= 'Correo Electrónico',
        required=False
    )
    
    civil_status = forms.ChoiceField(
        choices= CIVIL_STATUS,
        label= "Estado Civil",
        initial="Soltero"
    )
    
    dni = forms.IntegerField(
        label= "DNI",
    )
    
    profession = forms.CharField(
        label= "Profesion",
        required=False
    )
    
    address = forms.CharField(
        label= "Domicilio",
        required=False
    )
    
    job_address = forms.CharField(
        label= "Domicilio Laboral",
        required=False
    )
    
    class Meta:
        model = Guarantor
        fields = "__all__"
        exclude = ["credit"]

    def clean_dni(self):
        """
        Validar que el DNI sea válido
        """
        dni = self.cleaned_data.get('dni')
        
        if self.prefix == 'guarantor':
            if len(str(dni)) < 7 or  len(str(dni)) >= 15:
                raise forms.ValidationError("El DNI debe contener como mínimo 7 y máximo 15 caracteres")

            existing_guarantor = Guarantor.objects.filter(dni=dni).first()
            if Guarantor.objects.filter(dni=dni).exists():
                if existing_guarantor != self.instance :
                    raise forms.ValidationError("El DNI {} ya registra".format(dni))

        return dni

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if self.prefix == 'guarantor':
            if len(first_name) < 3:
                raise forms.ValidationError("El nombre debe contener al menos 3 caracteres")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if self.prefix == 'guarantor':
            if len(last_name) < 3:
                raise forms.ValidationError("El apellido debe contener al menos 3 caracteres")
        return last_name

    def clean_email(self):
        """
        Validar que el correo electrónico sea válido
        """
        email = self.cleaned_data.get('email')

        # Validar formato de correo electrónico
        if self.prefix == 'guarantor' and len(email) > 0:
            try:
                validate_email(email)
            except forms.ValidationError:
                raise forms.ValidationError("Ingrese un correo electrónico válido")

            existing_guarantor = Guarantor.objects.filter(email=email).first()

            if Guarantor.objects.filter(email=email).exists():
                if existing_guarantor != self.instance :
                    raise forms.ValidationError("El correo: %s ya esta en uso" % email)

        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
        # Eliminar validación requerida
        if  kwargs["prefix"] == 'credit_created':
            for field in self.fields.values():
                field.required = False    
        
#FORMULARIO PARA UPDATES
#-----------------------------------------------------------------
class GuarantorUpdateForm(forms.ModelForm):
        
    CIVIL_STATUS = (
        ('Soltero','Soltero'),
        ('Casado', 'Casado'),
        ('Viudo', 'Viudo'),
        ('Divorciado', 'Divorciado')
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
        required=False,
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
        model = Guarantor
        fields = "__all__"
        exclude = ["credit"]

    
    def clean_dni(self):
        """
        Validar que el DNI sea válido
        """
        dni = self.cleaned_data.get('dni')
        if len(str(dni)) < 7 or  len(str(dni)) >= 15:
            raise forms.ValidationError("El DNI debe contener como mínimo 7 y máximo 15 caracteres")

        existing_guarantor = Guarantor.objects.filter(dni=dni).first()
        if Guarantor.objects.filter(dni=dni).exists():
            if existing_guarantor != self.instance :
                raise forms.ValidationError("El DNI {} ya registra".format(dni))

        return dni

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) < 3:
            raise forms.ValidationError("El nombre debe contener al menos 3 caracteres")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) < 3:
            raise forms.ValidationError("El apellido debe contener al menos 3 caracteres")
        return last_name

    def clean_email(self):
        """
        Validar que el correo electrónico sea válido
        """
        email = self.cleaned_data.get('email')

        # Validar formato de correo electrónico
        try:
            validate_email(email)
        except forms.ValidationError:
            raise forms.ValidationError("Ingrese un correo electrónico válido")

        existing_guarantor = Guarantor.objects.filter(email=email).first()

        if Guarantor.objects.filter(email=email).exists():
            if existing_guarantor != self.instance :
                raise forms.ValidationError("El correo: %s ya esta en uso" % email)

        return email


    def __init__(self, *args, **kwargs):
        super(GuarantorUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})

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
        required=False,
        widget=forms.NumberInput(
        attrs={'type':'number'}
        )
    )
    
    phone_type_g = forms.ChoiceField(
        choices= PhoneType,
        label="Tipo"
    )
    
    class Meta:
        model = PhoneNumberGuarantor
        fields = ('phone_number_g', 'phone_type_g')
    
    def clean_phone_number_g(self):
        """
        Validacion de numero de telefono.
        """
        phone_number_g = self.cleaned_data.get('phone_number_g')
        if phone_number_g is None or phone_number_g == '':
            return None
        elif not phone_number_g.isdigit():
            raise forms.ValidationError("El número de teléfono debe contener solo dígitos")
        elif len(phone_number_g) > 0 and (len(phone_number_g) < 8 or len(phone_number_g) > 20):
            raise forms.ValidationError("El numero debe contener como minimo 8 y 15 digitos")
        return phone_number_g    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
        # Eliminar validación requerida
        for field in self.fields.values():
            field.required = False                

#------------------------------------------------------------------
PhoneNumberFormSetG = inlineformset_factory(
    Guarantor, 
    PhoneNumberGuarantor, 
    form = PhoneNumberFormGuarantor,
    extra= 3,
    can_delete= False,
)

PhoneNumberFormSetGUpdate = inlineformset_factory(
    Guarantor, 
    PhoneNumberGuarantor, 
    form = PhoneNumberFormGuarantor,
    extra= 0,
    can_delete= False,
)