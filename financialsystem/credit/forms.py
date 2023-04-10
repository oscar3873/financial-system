from datetime import datetime
from django import forms

from commissions.models import Interest
from adviser.models import Adviser
from .models import *

#FORMULARIO PARA LA CREACION DEL CLIENTE
#------------------------------------------------------------------
class CreditForm(forms.ModelForm):

    is_old_credit = forms.BooleanField(
        label='¿Credito Antigüo?',
        help_text="Tildar el campo para SI",
        required=False,
    )

    interest = forms.IntegerField(
        label= "Intereses",
        required= True,
        initial= Interest.objects.first().interest_credit if not Interest.DoesNotExist else 40,
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
        min_value=0,
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

    has_pay_stub = forms.BooleanField(
        label='Recibo de sueldo',
        required=False
    )

    class Meta:
        model = Credit
        fields = ["is_old_credit","amount", "interest", "installment_num", "start_date", "has_pay_stub",'adviser']

    #ASOCIACION DE CRYSPY FORM
    def __init__(self, *args, **kwargs):
        
        self.adviser = kwargs["initial"].pop('adviser')
        super().__init__(*args, **kwargs)
        
        self.fields['adviser'].initial = self.adviser 

        for field_name in self.fields:
            field = self.fields.get(field_name)
            if not isinstance(field, forms.BooleanField):
                field.widget.attrs.update({'class': 'form-control'})

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
            attrs={'class': 'form-control bg-primary text-warning font-weight-bold', 'readonly': 'readonly', 'style': 'font-size: 2rem; border: none; user-select: none; outline: none; -webkit-box-shadow: none; -moz-box-shadow: none; box-shadow: none; cursor: default;'}
        )
    )

    installment_amount = forms.CharField(
        label= "Valor de cuota $",
        widget=forms.TextInput(
            attrs={'class': 'form-control bg-primary text-warning font-weight-bold', 'readonly': 'readonly', 'style': 'font-size: 2rem; border: none; user-select: none; outline: none; -webkit-box-shadow: none; -moz-box-shadow: none; box-shadow: none; cursor: default;'}
        )
    )

    installment_num = forms.ChoiceField(
        label= "Numero de Cuotas",
        choices=CHOICES,
        initial=CHOICES[0],
        required= True,
        widget=forms.Select()
    )

    class Meta:
        model = Refinancing
        fields = ["amount", "installment_num"]


    def __init__(self,credit,*args, **kwargs):
        """
        Formulario de Refinanciacion. Mediante 'checkboxs', selecciona cuotas a refiannciar.
        """
        super().__init__(*args, **kwargs)
        installments = credit.installments.exclude(condition__in=['Refinanciada', 'Pagada'])

        self.fields['amount'].widget.attrs['id'] = 'id_amount{}'.format(credit.pk)  # AGREGA ID PARA IDENTIFICACION EN .HTML >> JS
        self.fields['installment_num'].widget.attrs['id'] = 'id_installment_num{}'.format(credit.pk)    # AGREGA ID PARA IDENTIFICACION EN .HTML >> JS
        self.fields['installment_amount'].widget.attrs['id'] = 'id_installment_amount{}'.format(credit.pk)    # AGREGA ID PARA IDENTIFICACION EN .HTML >> JS
        
        for installment in installments:
            if installment == credit.installments.first():
                self.fields['cuota_%s' %str(installment.installment_number)] = forms.BooleanField(
                    label='Cuota %s%s' % (
                        installment.installment_number,
                        ' (intereses acumulados $ %s)' % installment.daily_interests if installment.daily_interests > 0 else ''),
                        required=True,
                        widget=forms.CheckboxInput(attrs={
                            "class": "form-check", 
                            "value": installment.amount, 
                            "data-form-id": "form_ref%s" % (credit.pk)
                        })
                    )
            else:
                self.fields['cuota_%s' %str(installment.installment_number)] = forms.BooleanField(
                   label='Cuota %s%s' % (
                        installment.installment_number,
                        ' (intereses acumulados $ %s)' % installment.daily_interests if installment.daily_interests > 0 else ''),
                        required=False,
                        widget=forms.CheckboxInput(attrs={
                            "class": "form-check", 
                            "value": installment.amount, 
                            "data-form-id": "form_ref%s" % (credit.pk)})
                    )


class RefinancingFormUpdate(forms.ModelForm):

    class Meta:
        model = Refinancing
        fields = ["amount", "interest", "installment_num", "start_date", "end_date", "payment_date"]
        widgets ={
            'start_date': forms.DateInput(attrs={'type': 'date'},format="%Y-%m-%d"),
            'end_date': forms.DateInput(attrs={'type': 'date'},format="%Y-%m-%d"),
            'payment_date': forms.DateInput(attrs={'type': 'date'},format="%Y-%m-%d"),
        }
        labels = {
            'installment_num':'Numero de cuotas',
            'interest':'Interes',
            'amount':'Monto',
            'start_date': 'Fecha de Inicio',
            'end_date': 'Fecha de Vencimiento',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})


class InstallmentUpdateForm(forms.ModelForm):

    class Meta:
        model = Installment
        fields = ['amount', 'daily_interests', 'porcentage_daily_interests', 'start_date', 'end_date', 'payment_date', 'condition']  
        labels = {
            'amount': 'Monto',
            'end_date': 'Fecha de Vencimiento',
            'start_date': 'Fecha de Inicio',
            'payment_date': 'Fecha de pago',
            'condition': 'Condición',
            'daily_interests' : 'Intereses generados',
            'porcentage_daily_interests' : 'Porcentaje de interes diario'
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'daily_interests': forms.NumberInput(attrs={'class': 'form-control'}),
            'porcentage_daily_interests': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control','type': 'date'}, format='%Y-%m-%d'),
            'end_date': forms.DateInput(attrs={'class': 'form-control','type': 'date'},format='%Y-%m-%d'),
            'start_date': forms.DateInput(attrs={'class': 'form-control','type': 'date'},format='%Y-%m-%d'),
        }


class InstallmentRefinancingUpdateForm(forms.ModelForm):
    
    class Meta:
        model = InstallmentRefinancing
        fields = ['amount', 'daily_interests', 'porcentage_daily_interests', 'start_date', 'end_date', 'payment_date', 'condition']  
        labels = {
            'amount': 'Monto',
            'end_date': 'Fecha de Vencimiento',
            'start_date': 'Fecha de Vencimiento',
            'payment_date': 'Fecha de pago',
            'condition': 'Condición',
            'daily_interests' : 'Intereses generados',
            'porcentage_daily_interests' : 'Porcentaje de interes diario'

        }
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly':True}),
            'daily_interests': forms.NumberInput(attrs={'class': 'form-control'}),
            'porcentage_daily_interests': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control','type': 'date'}, format= '%Y-%m-%d'),
            'end_date': forms.DateInput(attrs={'class': 'form-control','type': 'date'},format= '%Y-%m-%d'),
            'start_date': forms.DateInput(attrs={'class': 'form-control','type': 'date'},format='%Y-%m-%d'),
        }
        auto_id = True


#-------------------------------------------FORMS UPDATE--------------------------------
class CreditUpdateForm(forms.ModelForm):

    interest = forms.IntegerField(
        label= "Intereses",
        required= True,
        initial= Interest.objects.first().interest_credit if not Interest.DoesNotExist else 40,
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
    
    adviser = forms.ModelChoiceField(
        label= 'Asesor',
        queryset= Adviser.objects.all(),
    )

    class Meta:
        model = Credit
        fields = ["amount", "interest", "installment_num", "start_date",'adviser']
        widgets ={
            'start_date': forms.DateInput(attrs={'type': 'date'},format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'class': 'form-control'})
