from datetime import datetime
from decimal import Decimal
from django import forms
from credit.models import Installment

from payment.models import Payment

class PaymentForm(forms.ModelForm):
    MONEY_TYPE = (
        ('PESOS', 'PESOS'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRANSFER', 'TRANSFER'),
        ('CREDITO', 'CREDITO'),
        ('DEBITO', 'DEBITO'),
    )

    amount = forms.CharField(
        label= "Total a Pagar $",
        required=False,
        widget=forms.TextInput(
            attrs={'class':'form-control bg-primary text-warning font-weight-bold', 'readonly': 'readonly', 'style': 'font-size: 2rem; border: none; user-select: none; outline: none; -webkit-box-shadow: none; -moz-box-shadow: none; box-shadow: none; cursor: default;'}
        )
    )

    amount_paid = forms.DecimalField(
        label='Pago por cantidad', 
        min_value=0,
        help_text="Recomendable pagar el 50% de la deuda",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    payment_date = forms.DateField(
        label="Fecha de Pago",
        required=True,
        widget=  forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'value': datetime.now().date()
            })
    )

    payment_method = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control m-auto'}),
        label="Forma de Pago",
        choices=MONEY_TYPE,
        required=True
    )
    
    class Meta:
        model = Payment
        fields = ["amount", "payment_date", "payment_method"]
    
    def __init__(self,installments,*args, **kwargs):
        """
        Formulario de Pagos. Mediante 'checkboxs', selecciona cuotas a pagar.
        """
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.prefix = "payment"

        self.fields['amount_paid'].initial = Decimal((sum([installment.amount for installment in installments]))/2)

        if installments.count() > 0:
            for installment in installments:
                daily_interests = ' (con interés {})'.format(installment.daily_interests) if installment.daily_interests > 0 else ''

                if isinstance(installment,Installment):
                    form = "form_payment%s" % installment.credit.pk
                    self.fields['amount'].widget.attrs.update({'id': "id_payment-amount%s" % installments.first().credit.pk}) # AGREGA ID PARA IDENTIFICACION EN .HTML >> JS
                    self.fields['amount_paid'].widget.attrs.update({'id': "id_amount_paid%s" % installments.first().credit.pk})
                else:
                    form = "form_payment%s" % installment.refinancing.pk
                    self.fields['amount'].widget.attrs.update({'id': "id_payment-amount%s" % installment.refinancing.pk}) # AGREGA ID PARA IDENTIFICACION EN .HTML >> JS
                    self.fields['amount_paid'].widget.attrs.update({'id': "id_amount_paid%s" % installment.refinancing.pk})
 
                attrs = {"value": installment.amount + installment.daily_interests, "id":form}
                
                # if installment == installments.first():
                self.fields['Cuota %s %s' % (str(installment.installment_number), daily_interests)] = forms.BooleanField(
                    label='Cuota %s %s' % (str(installment.installment_number), daily_interests),required=False,
                    widget=forms.CheckboxInput(attrs=attrs)
                )
                # else:
                #     self.fields['Cuota %s %s' % (str(installment.installment_number), daily_interests)] = forms.BooleanField(
                #         label='Cuota %s %s' % (str(installment.installment_number), daily_interests),required=False,
                #         widget=forms.CheckboxInput(attrs=attrs)
                #     )