import datetime
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

from payment.models import Payment
from credit.models import Installment

def all_properties_paymnet():
    return ['Monto','Forma de Pago','Detalle','Fecha']

def payment_create(payment, installment):
    payment_dict = {
        'amount': payment.amount,
        'payment_date': payment.payment_date,
        'adviser': payment.adviser,
        'payment_method': payment.payment_method,
    }
    
    if isinstance(installment, Installment):
        payment_dict['installment'] = installment
        payment_dict['detail'] = 'COBRO CUOTA %s - CLIENTE %s - ASESOR %s' % (installment.installment_number,installment.credit.client, payment.adviser)
    else:
        payment_dict['installment_ref'] = installment
        payment_dict['detail'] = 'COBRO CUOTA REFINANCIADA %s - CLIENTE %s - ASESOR %s' % (installment.installment_number,installment.refinancing.installment_ref.last().credit.client, payment.adviser)
        
    Payment.objects.create(**payment_dict)


def pay_installment(request, payment, installments, amount_paid):
    """
    Metodo para pagos parciales: SOLO PARA CUOTAS VENCIDAS Y EL PAGO DEBE
    SER MAYOR O IGUAL AL 50% DE LA DEUDA (INTERESES + VALOR DE CUOTA)
    """
    if not installments:
        messages.warning(request, 'Este crédito no puede poseer el beneficio "pausa por 15 días"', 'warning')
        return

    amount_list = installments.values_list('amount', flat=True)
    if amount_paid < sum(amount_list) / 2:
        messages.error(request, 'No puede recibir pago menor al 50% de la deuda!', 'danger')
        return

    for installment in installments:
        if installment.amount <= amount_paid:
            print('############PAGADA COMPLETA')
            installment.condition = 'Pagada'
            installment.payment_date = payment.payment_date
            installment.save()

            payment_create(payment, installment)
            amount_paid -= installment.amount

        elif amount_paid >= Decimal(installment.amount / Decimal(2)):
            print('########## PAGO PARCIAL')
            payment.amount = amount_paid # PARA RELAIZAR EL MOVIMIENTO
            installment.amount -= payment.amount
            installment.original_amount = installment.amount # PARA ACTUALIZAR EL MONTO A DEVOLVER EN BASE AL SALDO LUEGO DEL 50%
            fifteen_later_din(installment)
            payment_create(payment, installment) # PARA RELAIZAR EL MOVIMIENTO

            amount_paid = 0

        else:  # SI EL RESTANTE NO SUPERA LOS 50% DE LA DEUDA
            print("######### DISMINUYE MONTO SOBRANTE")
            installment.amount -= amount_paid # DISMINUYE EL MONTO
            
            fifteen_later_din(installment)
            amount_paid = 0


def fifteen_later_din(installment):
    """
    Mueve la fecha vencimiento 15 dias despues (por beneficio de pago del 50% de la deuda)
    """
    installment.end_date = datetime.date.today() + datetime.timedelta(days=15)
    installment.save()
