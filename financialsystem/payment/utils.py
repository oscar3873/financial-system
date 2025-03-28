import os
import datetime
from django.template.loader import get_template
from django.http import Http404, HttpResponse
from weasyprint import HTML
from decimal import Decimal
from django.contrib import messages
from django.conf import settings

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
        
    return Payment.objects.create(**payment_dict)


def pay_installment(request, payment, installments, amount_paid):
    """
    Metodo para pagos parciales: SOLO PARA CUOTAS VENCIDAS Y EL PAGO DEBE
    SER MAYOR O IGUAL AL 50% DE LA DEUDA (INTERESES + VALOR DE CUOTA)
    """
    if not installments:
        messages.warning(request, 'Este crédito no puede poseer el beneficio "pausa por 15 días"', 'warning')
        return

    # amount_list = installments.values_list('amount', flat=True)
    # if amount_paid < sum(amount_list) / 2:
    #     messages.error(request, 'No puede recibir pago menor al 50% de la deuda!', 'danger')
    #     return

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
            installment.daily_interests = 0
            fifteen_later_din(installment)
            payment_create(payment, installment) # PARA RELAIZAR EL MOVIMIENTO

            amount_paid = 0

        else:  # SI EL RESTANTE NO SUPERA LOS 50% DE LA DEUDA
            print("######### DISMINUYE MONTO SOBRANTE")
            payment.amount = amount_paid # PARA RELAIZAR EL MOVIMIENTO
            installment.amount -= amount_paid # DISMINUYE EL MONTO
            installment.daily_interests = max(installment.daily_interests - amount_paid, 0) # PARA ACTUALIZAR EL MONTO A DEVOLVER EN BASE AL SALDO LUEGO DEL 50%
            installment.save()

            payment_create(payment, installment) # PARA RELAIZAR EL MOVIMIENTO
            amount_paid = 0


def fifteen_later_din(installment):
    """
    Mueve la fecha vencimiento 15 dias despues (por beneficio de pago del 50% de la deuda)
    """
    installment.end_date = datetime.date.today() + datetime.timedelta(days=15)
    installment.save()

def generate_pdf_receipt(request, context):
    # Agrega la ruta absoluta a tus estáticos:
    base_static_url = f"file://{settings.STATIC_ROOT}/"
    context['base_static_url'] = base_static_url

    template = get_template('payment/recibo.html')
    html_string = template.render(context)
    
    # Usa una base_url adecuada para WeasyPrint, por ejemplo la ruta absoluta a tus estáticos:
    html = HTML(string=html_string, base_url=base_static_url)
    pdf = html.write_pdf()
    with open('/tmp/recibo_debug.html', 'w') as f:
        f.write(html_string)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="recibo.pdf"'
    return response

def download_receipt(payment):
    """
    Descarga el comprobante de pago si existe.
    """
    receipt = payment.receipt
    print('ESTE ES EL RECIBO', receipt)
    if not receipt or not receipt.name:  # Verifica que el recibo existe y tiene un nombre de archivo
        raise Http404("El recibo no está disponible.")

    try:
        response = HttpResponse(receipt.open('rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(receipt.name)}"'
        return response
    except Exception as e:
        print(f"Error al descargar el recibo: {e}")
        raise Http404("No se pudo descargar el recibo.")