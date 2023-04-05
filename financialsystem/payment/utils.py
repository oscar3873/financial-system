import datetime
from django.core.exceptions import ObjectDoesNotExist
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
    }
    
    if isinstance(installment, Installment):
        payment_dict['installment'] = installment
        payment_dict['detail'] = 'COBRO CUOTA %s - CLIENTE %s - ASESOR %s' % (installment.installment_number,installment.credit.client, payment._adviser)
    else:
        payment_dict['installment_ref'] = installment
        payment_dict['detail'] = 'COBRO CUOTA REFINANCIADA %s - CLIENTE %s - ASESOR %s' % (installment.installment_number,installment.refinancing.installment_ref.last().credit.client, payment._adviser)
        
    Payment.objects.create(**payment_dict)


def pay_installment(payment, installments, amount_paid):
    """
    Metodo para pagos parciales: a travez de un monto X, realiza el pago de la cuota que encaja
    y realiza la disminucion de la cuota a pagar en caso que no supere el monto de la cuota
    """
    for i, installment in enumerate(installments):
        if installment.amount <= amount_paid:
            print(f'############ Cuota {i+1} PAGADA COMPLETA')
            installment.condition = 'Pagada'
            installment.payment_date = payment.payment_date
            installment.save()

            payment_create(payment, installment)
            amount_paid -= installment.amount

        else:
            print(f"######### Cuota {i+1} ACUMULA MONTO A CUOTA {len(installments)}")
            installment.amount = 0
            installment.condition = 'Pagada'
            installment.payment_date = payment.payment_date
            installment.save()

            payment_create(payment, installment)
            debt = amount_paid + sum([inst.original_amount for inst in installments[i:]])
            last_inst = installments[-1]
            last_inst.original_amount += debt
            fifteen_later_din(last_inst)
            make_paid(last_inst, payment)
            amount_paid = 0
            break
        

def fifteen_later_din(installment):
    fifteen_later = datetime.date.today() + datetime.timedelta(days=15)
    installment.end_date = fifteen_later
    installment.save()

def make_paid(installment,payment):
    installment.condition = 'Pagada'
    installment.payment_date = payment.payment_date
    installment.save()
