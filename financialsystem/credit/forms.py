from datetime import datetime
from django import forms
from .models import Credit, Installment, Refinancing
from django.forms import inlineformset_factory

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
        fields = ["amount", "installment_num_refinancing"]


    def __init__(self,credit,*args, **kwargs):
        """
        Formulario de Refinanciacion. Mediante 'checkboxs', selecciona cuotas a refiannciar.
        """
        super().__init__(*args, **kwargs)
        installments = credit.installments.exclude(condition__in=['Refinanciada', 'Pagada'])
        for installment in installments:
            if installment == credit.installments.first():
                self.fields['Cuota %s' %str(installment.installment_number)] = forms.BooleanField(
                    label='Cuota %s%s' % (
                        installment.installment_number,
                        ' (intereses acumulados $ %s)' % installment.daily_interests if installment.daily_interests > 0 else ''),
                        required=True,
                        widget=forms.CheckboxInput(attrs={"value": installment.amount+installment.daily_interests, "data-form-id": "form_ref"})
                    )
            else:
                self.fields['Cuota %s' %str(installment.installment_number)] = forms.BooleanField(
                   label='Cuota %s%s' % (
                        installment.installment_number,
                        ' (intereses acumulados $ %s)' % installment.daily_interests if installment.daily_interests > 0 else ''),
                        required=False,
                        widget=forms.CheckboxInput(attrs={"value": installment.amount+installment.daily_interests, "data-form-id": "form_ref"})
                    )
    

class InstallmentUpdateForm(forms.ModelForm):

    class Meta:
        model = Installment
        fields = ['amount', 'end_date', 'payment_date', 'condition']  
        labels = {
            'amount': 'Monto',
            'end_date': 'Fecha de Vencimiento',
            'payment_date': 'Fecha de pago',
            'condition': 'Condición'
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly':True}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'id': 'payment_date','type': 'date'}, format='%Y-%m-%d'),
            'end_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'id': 'end_date','type': 'date'},format='%Y-%m-%d'),
        }
        auto_id = True

class InstallmentRefinancingForm(forms.ModelForm):
    
    class Meta:
        model = Installment
        fields = ['amount', 'end_date', 'payment_date', 'condition']
        labels = {
            'amount': 'Monto',
            'end_date': 'Fecha de Vencimiento',
            'payment_date': 'Fecha de pago',
            'condition': 'Condición'
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly':True}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'id': 'payment_date','type': 'date'}, format= '%Y-%m-%d'),
            'end_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'id': 'end_date','type': 'date'},format= '%Y-%m-%d'),
        }
        auto_id = True



#--------------------------FORMSET FOR CREDIT AND CREDIT'S INSTALMMENTS UPDATE----------------------------------------

class CreditWithInstallmentsForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = ['is_active', 'is_paid', 'is_old_credit', 'condition', 'credit_interest', 'amount', 'installment_num', 'start_date', 'end_date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.installment_formset = InstallmentFormSet(instance=self.instance)

InstallmentFormSet = inlineformset_factory(
    Credit, 
    Installment, 
    form=InstallmentUpdateForm, 
    )
#-------------------------------------------------------------------------------------------------   