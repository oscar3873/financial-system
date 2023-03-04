from payment.models import Payment


def payment_create(payment, installment):
    Payment.objects.create(
        amount=payment.amount,
        paid_date=payment.paid_date,
        installment = installment,
        adviser=payment._adviser,
        payment_method = payment.payment_method,
        detail = 'COBRO CUOTA %s - CLIENTE %s - ASESOR %s' % (installment.installment_number, installment.credit.client, payment._adviser)
    )