from datetime import datetime
from django import forms
from crispy_forms.helper import FormHelper
from .models import Credit, Refinancing

#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------
class CreditForm(forms.ModelForm):
    
    credit_interest = forms.IntegerField(
        label= "Intereses",
        required= True,
        initial= 40,
        min_value= 0,
        max_value= 100
    )
    
    amount = forms.DecimalField(
        label= "Monto Solicitado",
        required= True,
    )
    
    installment_num = forms.IntegerField(
        label= "Cuotas",
        required= True,
        min_value=1,
        max_value=12,
    )
    
    start_date = forms.DateTimeField(
        label="Fecha de Entrada",
        required=True,
        widget=  forms.DateInput(attrs={
            'type': 'date',
            'value': datetime.now().date()
            })
    )
    class Meta:
        model = Credit
        fields = ["amount", "credit_interest", "installment_num", "start_date"]
    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper

#-----------------------------------------------------------------
class RefinancingForm(forms.ModelForm):
    CHOICES = [
        (3,"3 Cuotas"),
        (6,"6 Cuotas"),
        (9,"9 Cuotas"),
        (12,"12 Cuotas"),
    ]
    
    amount = forms.CharField(
        label= "Total a Pagar $",
        widget=forms.TextInput(
            attrs={'readonly': 'readonly', 'style': 'border: none; user-select: none; outline: none; -webkit-box-shadow: none; -moz-box-shadow: none; box-shadow: none; cursor: default;'}
        )
    )


    installment_num_refinancing = forms.ChoiceField(
        label= "Numero de Cuotas",
        choices=CHOICES,
        initial=CHOICES[0],
        required= True,
    )

    class Meta:
        model = Refinancing
        fields = ["installment_num_refinancing","amount"]


    def __init__(self,credit,*args, **kwargs):
        super().__init__(*args, **kwargs)
        excludes = ['Refinanciada', 'Pagada']
        installments = credit.installment.exclude(condition__in=excludes)

        for installment in installments:
            if installment == credit.installment.first():
                self.fields['Cuota %s' %str(installment.installment_number)] = forms.BooleanField(
                    label='Cuota %s (intereses acumulados $ %s)' % (installment.installment_number, installment.daily_interests),required=True,
                    widget=forms.CheckboxInput(attrs={"value": installment.amount+installment.daily_interests})
                )
            else:
                self.fields['Cuota %s' %str(installment.installment_number)] = forms.BooleanField(
                    label='Cuota %s (intereses acumulados $ %s)' % (installment.installment_number, installment.daily_interests),required=False,
                    widget=forms.CheckboxInput(attrs={"value": installment.amount+installment.daily_interests})
                )
        