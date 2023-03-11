from payment.models import Payment
from credit.models import Installment

def payment_create(payment, installment):
    payment_dict = {
        'amount': payment.amount,
        'payment_date': payment.payment_date,
        'adviser': payment._adviser,
        'payment_method': payment.payment_method
    }
    if isinstance(installment, Installment):
        payment_dict['detail'] = 'COBRO CUOTA %s - CLIENTE %s - ASESOR %s' % (installment.installment_number,installment.credit.client, payment._adviser)
    else:
        payment_dict['detail'] = 'COBRO CUOTA REFINANCIADA %s - CLIENTE %s - ASESOR %s' % (installment.installment_number,installment.refinancing.installment_ref.last().credit.client, payment._adviser)
        
    Payment.objects.create(**payment_dict)
