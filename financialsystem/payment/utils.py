from payment.models import Payment
from credit.models import Installment

def all_properties_paymnet():
    return ['Monto','Forma de Pago','Detalle','Fecha']

def payment_create(payment, installment):
    payment_dict = {
        'amount': payment.amount,
        'payment_date': payment.payment_date,
        'adviser': payment._adviser,
        'payment_method': payment.payment_method,
        'installment': installment
    }
    if isinstance(installment, Installment):
        payment_dict['detail'] = 'COBRO CUOTA %s - CLIENTE %s - ASESOR %s' % (installment.installment_number,installment.credit.client, payment._adviser)
    else:
        payment_dict['detail'] = 'COBRO CUOTA REFINANCIADA %s - CLIENTE %s - ASESOR %s' % (installment.installment_number,installment.refinancing.installment_ref.last().credit.client, payment._adviser)
        
    Payment.objects.create(**payment_dict)


def pay_installment(payment, installments, amount_paid):
    """
    Metodo para pagos parciales: a travez de un monto X, realiza el pago de la cuota que encaja
    y realiza la disminucion de la cuota a pagar en caso que no supere el monto de la cuota
    """
    
    for installment in installments:
        if installment.amount <= amount_paid:
            installment.condition = 'Pagada'
            installment.is_paid_installment = True
            installment.payment_date = payment.payment_date
            print("AQUIIIII")
            installment.save()

            payment_create(payment, installment)
            amount_paid -= installment.amount

        elif amount_paid > 0:
            payment.amount = amount_paid
            installment.amount -= payment.amount
            installment.save()
            
            payment_create(payment, installment)
            amount_paid = 0