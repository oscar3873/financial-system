from django import forms
from crispy_forms.helper import FormHelper

from payment.models import Payment

class PaymentForm(forms.ModelForm):
    
    
    class Meta:
        model = Payment
        fields = "__all__"
        exclude = ["installment"]
    
    def __init__(self, *args, **kwargs):
        credit = kwargs.pop("credit", None)
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper
        excludes = ['Refinanciada', 'Pagada']
        installments = credit.installment.exclude(condition__in=excludes)
        if installments.count() > 0:
            for installment in installments:
                if installment == installments.first():
                    self.fields['Cuota %s' %str(installment.installment_number)] = forms.BooleanField(label='Cuota %s' % (installment.installment_number),required=True)
                else:
                    self.fields['Cuota %s' %str(installment.installment_number)] = forms.BooleanField(label='Cuota %s' % (installment.installment_number),required=False)