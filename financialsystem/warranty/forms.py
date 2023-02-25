from django import forms
from crispy_forms.helper import FormHelper
from warranty.models import Warranty
from clients.models import Client
#FORMULARIO PARA LA CREACION DEL EMPEÑO
#------------------------------------------------------------------
class WarrantyForm(forms.ModelForm):
    
    ARTICLE_STATE = (
        ('NUEVO','NUEVO'),
        ('USADO:COMO NUEVO', 'USADO:COMO NUEVO'),
        ('USADO:MUY BUENO', 'USADO:MUY BUENO'),
        ('USADO:BUENO', 'USADO:BUENO'),
        ('USADO:ACEPTABLE', 'USADO:ACEPTABLE'),
        ('USADO:REACONDICIONADO', 'USADO:REACONDICIONADO'),
        ('USADO:MUCHO USO', 'USADO:MUCHO USO'),
    )
    
    article = forms.CharField(
        label = 'Articulo',
        required=True,
    )
    
    purchase_papers = forms.BooleanField(
        label= 'Papeles',
        required=False,
        initial= False,
    )
    
    client = forms.ModelChoiceField(
        queryset= Client.objects.all(),
        initial= Client.objects.last(),
        required= True,
        label= "Cliente"
    )

    state = forms.ChoiceField(
        choices= ARTICLE_STATE,
        required=True,
        label= "Estado"
    )
    
    brand = forms.CharField(
        label= "Marca",
        required= True,
    )

    model = forms.CharField(
        label= "Modelo",
        required= True,
    ) 
    
    accessories = forms.CharField(
        label= "Accesorios",
        required= True,
    )

    
    class Meta:
        model = Warranty
        fields = "__all__"
    
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper