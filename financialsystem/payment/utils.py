import datetime
from decimal import Decimal
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
    for installment in installments:
        if installment.amount <= amount_paid:
            print('############PAGADA COMPLETA')
            installment.condition = 'Pagada'
            installment.payment_date = payment.payment_date
            installment.save()

            payment_create(payment, installment)
            amount_paid -= installment.amount

        elif amount_paid >= Decimal(installment.amount/Decimal(2)):
            print('########## PAGO PARCIAL')
            payment.amount = amount_paid # MOVIMIENTO
            installment.amount -= payment.amount
            
            fifteen_later_din(installment,False)
            payment_create(payment, installment) # MOVIMIENTO
            amount_paid = 0
        
        else:# SI EL RESTANTE NO SUPERA LOS 50% DE LA DEUDA
            print("######### ACUMULA MONTO A NEXT INST.")
            amount_base = amount_paid + installment.amount
            amount_org = installment.amount
            try:
                next_inst = installments.get(installment_number = installment.installment_number+1)
                print('########## try 1')
                next_inst.amount += amount_base
                print('########## try 2')
                next_inst.original_amount += amount_org
                print('########## try 3')
                fifteen_later_din(next_inst)
                print('########## try 4')
                make_paid(installment,payment)
                print('########## try 5')

            except ObjectDoesNotExist:
                print('########### EXCEPT')
                installment.amount += amount_base
                installment.original_amount += amount_org
                fifteen_later_din(installment)
            amount_paid = 0



def fifteen_later_din(installment, do=True):
    if do:
        fifteen_later = datetime.date.today() + datetime.timedelta(days=15)
        installment.end_date = fifteen_later
    installment.save()

def make_paid(installment,payment):
    installment.condition = 'Pagada'
    installment.payment_date = payment.payment_date
    installment.save()
