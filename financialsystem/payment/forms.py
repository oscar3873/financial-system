from datetime import datetime
from django import forms

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
        widget=forms.TextInput(
            attrs={'readonly': 'readonly', 'style': 'border: none; user-select: none; outline: none; -webkit-box-shadow: none; -moz-box-shadow: none; box-shadow: none; cursor: default;'}
        )
    )

    payment_date = forms.DateField(
        label="Fecha de Pago",
        required=True,
        widget=  forms.NumberInput(attrs={
            'type': 'date',
            'value': datetime.now().date()
            })
    )

    payment_method = forms.ChoiceField(
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
        if installments.count() > 0:
            for installment in installments:
                attrs = {"value": installment.amount + installment.daily_interests, "data-form-id":"form_payment"}
                if installment == installments.first():
                    self.fields['Cuota %s' %str(installment.installment_number)] = forms.BooleanField(
                        label='Cuota %s' % (installment.installment_number),required=True,
                        widget=forms.CheckboxInput(attrs=attrs)
                    )
                else:
                    self.fields['Cuota %s' %str(installment.installment_number)] = forms.BooleanField(
                        label='Cuota %s' % (installment.installment_number),required=False,
                        widget=forms.CheckboxInput(attrs=attrs)
                    )