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
    )
    
    purchase_papers = forms.BooleanField(
        label= 'Papeles de compra',
        initial= False,
    )
    
    state = forms.ChoiceField(
        choices= ARTICLE_STATE,
        label= "Estado"
    )
    
    brand = forms.CharField(
        label= "Marca",
    )

    model = forms.CharField(
        label= "Modelo",
    ) 
    
    accessories = forms.CharField(
        label= "Accesorios",
    )

    class Meta:
        model = Warranty
        fields = "__all__"
    
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
                
        for field in self.fields.values():
            field.required = False
            
        self.helper = FormHelper