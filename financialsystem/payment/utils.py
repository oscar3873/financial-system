import os
import datetime
from django.template.loader import get_template
from django.http import Http404, HttpResponse
from weasyprint import HTML
from decimal import Decimal
from django.contrib import messages
from django.conf import settings
from django.db.models import Sum
from dateutil.relativedelta import relativedelta

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
        'partial': payment.partial,
        'checked_discount': payment.checked_discount,
    }
    
    if isinstance(installment, Installment):
        payment_dict['installment'] = installment
        payment_dict['detail'] = generate_concept_text(installment, payments=[payment])

    else:
        payment_dict['installment_ref'] = installment
        payment_dict['detail'] = generate_concept_text(installment, payments=[payment])
        
    return Payment.objects.create(**payment_dict)


def pay_installment(request, payment, installments, amount_paid):
    """
    Metodo para pagos parciales: SOLO PARA CUOTAS VENCIDAS Y EL PAGO DEBE
    SER MAYOR O IGUAL AL 50% DE LA DEUDA (INTERESES + VALOR DE CUOTA)
    """
    if not installments:
        messages.warning(request, 'Este crédito no puede poseer el beneficio "pausa por 15 días"', 'warning')
        return []

    payments = []

    for installment in installments:
        print('######### CUOTA', installment.installment_number)
        print('######### MONTO A PAGAR', installment.amount)
        if installment.amount <= amount_paid:
            print('############PAGADA COMPLETA')
            amount_paid -= installment.amount
            payment.amount = installment.amount
            installment.condition = 'Pagada'
            installment.payment_date = payment.payment_date
            new_payment = payment_create(payment, installment)

            installment.amount = installment.original_amount
            installment.save()
            payments.append(new_payment)

        elif amount_paid >= Decimal(installment.original_amount / Decimal(2)):
            print('########## PAGO PARCIAL')
            payment.amount = amount_paid  # PARA RELAIZAR EL MOVIMIENTO
            payment.partial = True  # PARA RELAIZAR EL MOVIMIENTO
            installment.payment_date = payment.payment_date
            print(' ######### MONTO A PAGAR', installment.amount)
            installment.amount -= amount_paid
            print(' ######### MONTO A RESTANTE', installment.amount)
            installment.daily_interests = 0
            if installment.is_caduced_installment:
                fifteen_later_din(installment)
            else:    
                installment.save()
            new_payment = payment_create(payment, installment)
            payments.append(new_payment)
            amount_paid = 0
        else:
            print("######### DISMINUYE MONTO SOBRANTE")
            installment.payment_date = payment.payment_date
            payment.amount = amount_paid
            payment.partial = True
            installment.amount -= amount_paid
            installment.daily_interests = max(installment.daily_interests - amount_paid, 0)
            installment.save()

            new_payment = payment_create(payment, installment)
            payments.append(new_payment)
            amount_paid = 0
        if amount_paid <= 0:
            break

    return payments



def fifteen_later_din(installment):
    """
    Mueve la fecha vencimiento 15 dias despues (por beneficio de pago del 50% de la deuda)
    """
    installment.end_date = datetime.date.today() + datetime.timedelta(days=15)
    installment.save()
    
def get_installment_month_name(installment):
    """
    Retorna el mes y año correspondiente a una cuota basado en la fecha de inicio del crédito.
    Ej: "abril 2025"
    """
    credit_start = installment.credit.start_date
    cuota_n = installment.installment_number
    fecha_cuota = credit_start + relativedelta(months=cuota_n - 1)
    return fecha_cuota.strftime('%B')  # o '%B' si solo querés el mes

def update_installment_status(installment, payment_date):
    """
    Suma los pagos asociados a la cuota y, si el total es mayor o igual al monto de la cuota,
    actualiza la condición a 'Pagada'.
    """
    total_paid = installment.payments.aggregate(total=Sum('amount'))['total'] or 0
    if total_paid < installment.amount:
        porcentaje = (total_paid / installment.amount) * 100
        concepto = f"Pago parcial de cuota #{installment.installment_number} ({get_installment_month_name(installment)}) ({porcentaje:.0f}%)"
    else:
        concepto = f"Pago de cuota #{installment.installment_number} ({get_installment_month_name(installment)})"

def generate_concept_text(installment, payments=None):
    """
    Devuelve un string tipo:
    - "Pago de cuota #3 (Marzo)"
    - "Pago parcial de cuota #3 (Marzo)"
    """
    if isinstance(installment, Installment) :
        credit = installment.credit
        cuota_n = installment.installment_number
        cuota_mes = credit.start_date + relativedelta(months=cuota_n - 1)
        mes_str = cuota_mes.strftime('%B')  # o '%B' si solo querés el mes
        texto = f"Pago de cuota #{cuota_n} ({mes_str})"
    else:
        credit = installment.credit
        cuota_n = installment.installment_number
        cuota_mes = credit.start_date + relativedelta(months=cuota_n - 1)
        mes_str = cuota_mes.strftime('%B')
        texto = f"Pago de cuota #{cuota_n}(refinanciada) ({mes_str})"
        
    return texto

def generate_pdf_receipt(request, context):
    image_url = request.build_absolute_uri('/static/core/img/finanx_banner.png')
    context['image_url'] = image_url
    template = get_template('payment/recibo.html')
    html_string = template.render(context)
    return HttpResponse(html_string)

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