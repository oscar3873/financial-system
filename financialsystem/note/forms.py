from django import forms
from crispy_forms.helper import FormHelper
from note.models import Note
from django.contrib.auth.models import User

#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------
class NoteForm(forms.ModelForm):
    
    title = forms.CharField(
        label = 'Titulo',
        required=True,
    )
    content = forms.CharField(
        widget=forms.Textarea,
        label = 'Contenido de la nota',
        required=True,
    )
    user = forms.ModelChoiceField(
        queryset= User.objects.all(),
        initial= 1,
        required= True,
        label= 'Por',
    )
    
    class Meta:
        model = Note
        fields = ["title", "content", "user"]
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request') # Para obtener el usuario
        super(NoteForm, self).__init__(*args, **kwargs)
        self.fields["user"].initial = self.request.user.id
        self.helper = FormHelper