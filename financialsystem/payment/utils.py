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
        payment_dict['detail'] = f'COBRO CUOTA {installment.installment_number} - CLIENTE {installment.credit.client} - ASESOR {payment._adviser}',
        payment_dict['installment'] = installment
    else:
        payment_dict['detail'] = f'COBRO CUOTA {installment.installment_number} - CLIENTE {installment.refinancing.installment_ref.last().credit.client} - ASESOR {payment._adviser}',
        payment_dict['installment_ref'] = installment
        
    Payment.objects.create(**payment_dict)
#FICHAR 