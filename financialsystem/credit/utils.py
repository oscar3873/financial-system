from datetime import date, datetime
from decimal import Decimal
from cashregister.models import CashRegister, Movement
from commissions.models import Comission
from .models import Credit, Refinancing, Installment


def all_properties_credit():
        return ["Monto solicitado", "Monto a devolver", "Numero de cuotas", "Monto de las cuotas", "Estado", "Cliente", "Asesor", "Fecha de registro", "Fecha de Finalizacion"]


def refresh_condition():
    if Credit.objects.exists():
        credits_ok = Credit.objects.filter(condition='A Tiempo')
        cred_with_vencidas = credits_ok.filter(installments__end_date__date__lt=date.today())
        refinances = Refinancing.objects.filter(installments__end_date__lt=date.today())

        mi_lista = [cred_with_vencidas, refinances] if cred_with_vencidas and refinances else [cred_with_vencidas] if cred_with_vencidas else [refinances] if refinances else []
    
        for model in mi_lista:
            for obj_with_vencidas in model:
                for_refresh(obj_with_vencidas.installments.all())

        for credit in credits_ok:
            if credit.installments.filter(condition="Vencida").count() == credit.installments.count():
                credit.condition = "Vencido"
                credit.is_paid = True
                credit.save()

        refresh_installments_credits()


def for_refresh(obj_with_vencidas):
    for installment_ven in obj_with_vencidas.filter(end_date__date__lt=date.today()).filter(condition='A Tiempo'):
        if isinstance(installment_ven, Installment):
            client = installment_ven.credit.client
            if not installment_ven.is_refinancing_installment:
                installment_ven.condition = 'Vencida' # PORQUE LAS CUOTAS NORMALES TIENE UN CAMPO CONDITION
        else:
            client = installment_ven.refinancing.installment_ref.last().credit.client

        installment_ven.is_caduced_installment = True

        if installment_ven.lastup != date.today():
            dates = installment_ven.lastup
        else:
            dates = installment_ven.end_date.date()

        resto = (date.today() - dates).days
        client.score -= 5*resto
        installment_ven.daily_interests += resto * installment_ven.amount * Decimal(0.02)
        installment_ven.lastup = datetime.today()
        installment_ven.save()
        client.save()


def refresh_installments_credits():
    for model in [Refinancing, Credit]:
        credits_WPI = model.objects.filter(installments__condition='Pagada')
        for credit in credits_WPI:
            if credit.installments.filter(is_paid_installment=True).count() == credit.installments.count():
                if isinstance(credit, Credit):
                    credit.condition = 'Pagado'
                else:
                    for installment in credit.installment_ref.all():
                        installment.is_paid_installment = True
                        installment.condition = 'Pagada'
                        installment.payment_date = credit.installments.last().payment_date
                        installment.save()
                        credit.is_paid = True
                        credit.payment_date = credit.installments.last().payment_date

                credit.is_paid = True
                credit.save()

    

    