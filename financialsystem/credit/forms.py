from datetime import datetime
from django import forms
from .models import Credit, Installment, Refinancing

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
        fields = ['amount','is_caduced_installment','is_paid_installment','is_refinancing_installment','payment_date','end_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'id': 'payment_date','type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'id': 'end_date','type': 'date'}),
        }
        auto_id = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.payment_date:
            # print('#############')
            self.initial['payment_date'] = self.instance.payment_date.date().strftime('%Y-%m-%d')
        else:
            self.fields['payment_date'].initial = ''

        self.initial['end_date'] = self.instance.end_date.strftime('%Y-%m-%d')
        
        self.fields['is_caduced_installment'].label = '¿La cuota está vencida?'
        self.fields['is_paid_installment'].label = '¿La cuota está pagada?'
        self.fields['is_refinancing_installment'].label = '¿La cuota fue refinanciada?'
        self.fields['payment_date'].label = 'Fecha de pago'
        self.fields['end_date'].label = 'Fecha de Vencimiento'
        self.fields['amount'].label = 'Monto de la cuota'

        self.fields['amount'].widget.attrs['readonly'] = True


class InstallmentRefinancingForm(forms.ModelForm):

    class Meta:
        model = Installment
        fields = ['amount','is_caduced_installment','is_paid_installment','payment_date','end_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'id': 'payment_date','type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'id': 'end_date','type': 'date'}),
        }
        auto_id = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.payment_date:
            self.initial['payment_date'] = self.instance.payment_date.date().strftime('%Y-%m-%d')
        else:
            self.fields['payment_date'].initial = ''

        self.initial['end_date'] = self.instance.end_date.strftime('%Y-%m-%d')
        
        self.fields['is_caduced_installment'].label = '¿La cuota está vencida?'
        self.fields['is_paid_installment'].label = '¿La cuota está pagada?'
        self.fields['payment_date'].label = 'Fecha de pago'
        self.fields['end_date'].label = 'Fecha de Vencimiento'
        self.fields['amount'].label = 'Monto de la cuota'

        self.fields['amount'].widget.attrs['readonly'] = True



#------------------------------------------------------------------   NUEVOOOO
from django.forms import inlineformset_factory

# Creamos una clase de formulario para la entidad Credit
class CreditoForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = ['is_active', 'is_paid', 'is_old_credit', 'condition', 'credit_interest', 'amount', 'client', 'installment_num', 'start_date', 'end_date']

# Creamos una clase de formulario para la entidad Installment
class InstallmentoForm(forms.ModelForm):
    class Meta:
        model = Installment
        fields = ['installment_number', 'start_date', 'end_date', 'payment_date', 'condition', 'amount']



InstallmentFormSet = inlineformset_factory(
    Credit, 
    Installment, 
    form=InstallmentoForm, 
    extra=0
    )



class CreditWithInstallmentsForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = ['is_active', 'is_paid', 'is_old_credit', 'condition', 'credit_interest', 'amount', 'client', 'installment_num', 'start_date', 'end_date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.installment_formset = InstallmentFormSet(instance=self.instance)
#------------------------------------------------------------------   NUEVOOOO