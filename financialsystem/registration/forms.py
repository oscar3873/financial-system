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
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper
        
    def clean_email(self):
        email = self.cleaned_data.get("email")
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("El email ya esta registrado, prueba con otro.")
        return email