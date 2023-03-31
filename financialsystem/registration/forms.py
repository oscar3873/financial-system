from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper

class UserCreationFormWithEmail(UserCreationForm):
     email = forms.EmailField(
          label= 'Correo Electrónico',
          required=True,
     )
     username = forms.CharField(
          label = 'Nombre de Usuario',
          required=True,
     )
     first_name = forms.CharField(
          label = 'Nombre/s',
          required=True,
     )
     last_name = forms.CharField(
          label = 'Apellido/s',
          required=True,
     )
     password1 = forms.CharField(
          label = "Contraseña",
          required=True
     )
     password2 = forms.CharField(
          label = "Confirmar Contraseña",
          required=True
     )
     class Meta:
          model = User
          fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
          
     def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          for field_name in self.fields:
               field = self.fields.get(field_name)
               field.widget.attrs.update({'class': 'form-control'})
          self.helper = FormHelper
          
     def clean_email(self):
          email = self.cleaned_data.get("email")
          
          if User.objects.filter(email=email).exists():
               raise forms.ValidationError("El email ya esta registrado, prueba con otro.")
          return email
     
     def clean_first_name(self):
          name = self.cleaned_data.get("first_name")
          if len(name) < 3:
               raise forms.ValidationError("El Nombre debe contener por lo menos 3 caracteres")
          return name
    
     def clean_last_name(self):
        name = self.cleaned_data.get("last_name")
        if len(name) < 3:
            raise forms.ValidationError("El Apellido debe contener por lo menos 3 caracteres")
        return name