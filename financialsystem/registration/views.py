from .forms import  UserCreationFormWithEmail
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django import forms

# Create your views here.
class SignupView(CreateView):
    form_class = UserCreationFormWithEmail
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    
    def get_success_url(self) -> str:
        return reverse_lazy('login') + '?register'
    
    def get_form(self, form_class=None):
        form = super(SignupView, self).get_form()
        #Modifica en tiempo real
        form.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder':'Username'})
        form.fields["email"].widget = forms.EmailInput(attrs={'class': 'form-control mb-2', 'placeholder':'Email'})
        form.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control mb-2', 'placeholder':'Password'})
        form.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control mb-2', 'placeholder':'Repit Password'})
        return form