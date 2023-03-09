from datetime import datetime
from django import forms
from crispy_forms.helper import FormHelper
from warranty.models import Warranty, Sell
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

    detail = forms.CharField(
        label="Observaciones",
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
            

class SellForm(forms.ModelForm):
    MONEY_TYPE = [
        ('PESOS','PESOS'),
        ('USD','USD'),
        ('EUR', 'EUR'),
        ('TRANSFER','TRANSFERENCIA'),
        ('DEBITO','DEBITO'),
        ('CREDITO','CREDITO'),
        ]

    amount = forms.DecimalField(
        label="Monto",
        min_value=0,
        max_digits=15,
        decimal_places=2,
        required=True
    )

    payment_method = forms.ChoiceField(
        label="Forma de Pago",
        choices=MONEY_TYPE,
        required=True,
    )

    detail = forms.CharField(
        label="Observaciones",
        required=False,
    )

    sell_date = forms.DateTimeField(
        label="Fecha de Entrada",
        required=True,
        widget=  forms.DateInput(attrs={
            'type': 'date',
            'value': datetime.now().date()
            })
    )

    class Meta:
        model = Sell
        fields = "__all__"
        exclude = ["adviser","article", "commission"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
