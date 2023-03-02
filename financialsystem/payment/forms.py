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

    amount = forms.NumberInput(
        attrs={'value': '0'}
    )

    paid_date = forms.DateField(
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
        fields = [ "paid_date", "payment_method","amount"]
    
    def __init__(self,installments,*args, **kwargs):

        super(PaymentForm, self).__init__(*args, **kwargs)
        if installments.count() > 0:
            for installment in installments:
                if installment == installments.first():
                    self.fields['Cuota %s' %str(installment.installment_number)] = forms.BooleanField(
                        label='Cuota %s' % (installment.installment_number),required=True,
                        widget=forms.CheckboxInput(attrs={"value": installment.amount})
                    )
                else:
                    self.fields['Cuota %s' %str(installment.installment_number)] = forms.BooleanField(
                        label='Cuota %s' % (installment.installment_number),required=False,
                        widget=forms.CheckboxInput(attrs={"value": installment.amount})
                    )