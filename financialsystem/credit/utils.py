from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from django.http import JsonResponse
from django.db import transaction

from core.utils import round_to_nearest_hundred
from cashregister.utils import create_movement
from .models import Credit, Refinancing, Installment, InstallmentRefinancing
from clients.models import Client

from django.db.models import Count, Q, Max, F

import logging

BATCH_SIZE = 500

def all_properties_credit():
        return ["Monto solicitado", "Monto a devolver", "Numero de cuotas", "Monto de las cuotas", "Estado", "Cliente", "Asesor", "Fecha de registro", "Fecha de Finalizacion"]


def refresh_condition():
    logging.info("Init refresh_condition")
    if not Credit.objects.exists():
        return

    credits_ok = Credit.objects.exclude(condition="Pagado").only("id", "condition", "is_paid").prefetch_related("installments")

    vencidas_ids = set(
        credits_ok.filter(installments__end_date__lt=date.today()).values_list("id", flat=True)
    )
    refinances_ids = set(
        Refinancing.objects.filter(installments__end_date__lt=date.today()).values_list("id", flat=True)
    )

    vencidas_credits = Credit.objects.filter(id__in=vencidas_ids).prefetch_related("installments")
    vencidas_refinances = Refinancing.objects.filter(id__in=refinances_ids).prefetch_related("installments")

    models_to_refresh = list(vencidas_credits) + list(vencidas_refinances)

    with transaction.atomic():
        for model in models_to_refresh:
            installments = model.installments.exclude(
                condition__in=["Pagada", "Refinanciada"]
            ).filter(end_date__lt=date.today())

            process_installments_in_batches(installments)

        Credit.objects.filter(
            id__in=credits_ok.values_list("id", flat=True),
            installments__condition="Vencida",
        ).update(condition="Vencido", is_paid=False)
    refresh_installments_credits()


def process_installments_in_batches(installments):
    total = installments.count()
    for start in range(0, total, BATCH_SIZE):
        batch = installments[start : start + BATCH_SIZE]
        process_installment_batch(batch)


def process_installment_batch(installments):
    cont = 0
    for installment in installments:
        logging.info(f"installment condition:{installment.condition}")
        if isinstance(installment, Installment):
            logging.info("installment")
            credit = installment.credit
            client = credit.client
            if not installment.is_refinancing_installment:
                installment.condition = 'Vencida'
        elif isinstance(installment, InstallmentRefinancing):
            logging.info("installmentRefinancing")
            credit = installment.refinancing.credit
            client = credit.client
            installment.condition = 'Vencida'
        else:
            logging.info(f"installment type: {type(installment)}")
            credit = installment.refinancing.installment_ref.last().credit
            client = credit.client
            installment.condition = 'Vencida'

        # Actualiza las condiciones de la cuota
        installment.is_caduced_installment = True

        # Actualiza las fechas y otros cálculos
        logging.info(f"end_date: {installment.end_date}")
        if (installment.start_date + relativedelta(months=1)) < installment.end_date:
            installment.end_date = installment.lastup + relativedelta(days=(date.today() - installment.lastup).days)
            logging.info(f"New end_date: {installment.end_date}")
        resto = abs((date.today() - installment.lastup).days)
        end_date = installment.end_date.date() if isinstance(installment.end_date, datetime) else installment.end_date

        resto2 = abs((date.today() - end_date).days) if date.today() > end_date else 0
        logging.info(f"Resto 1: {resto} - Resto 2: {resto2}")
        daily_interes = (resto2 * installment.original_amount * installment.porcentage_daily_interests / 100)
        installment.daily_interests = daily_interes
        installment.amount = round_to_nearest_hundred(installment.original_amount + installment.daily_interests)
        logging.info("Nuevos valores")
        logging.info(f"daily_interes={daily_interes}")
        logging.info(f"installment.daily_interests={installment.daily_interests} = {resto2 * installment.original_amount * installment.porcentage_daily_interests / 100}")
        logging.info(f"installment.amount={installment.amount}")
        logging.info(f"installment.porcentage_daily_interests={installment.porcentage_daily_interests}")
        daily_interest = installment.porcentage_daily_interests

        installment.lastup = date.today()
        # Guarda las cuotas en un solo paso
        installment.save(update_fields=["condition", "is_caduced_installment", "lastup", "end_date", "daily_interests","amount"])

        # DISMINUCION DE SCORE EN BASE A INTERESES DIARIOS (MIENTRAS HAYA SIDO UN CREDITO ACTUAL)
        if isinstance(credit, Credit):
            if client.score - daily_interest * resto < 1:
                client.score = 0
            else:
                new_score = client.score - daily_interest * resto
                client.score = max(0, min(new_score, 1500))
        else:
            new_score = client.score - daily_interest * resto
            client.score = max(0, min(new_score, 1500))

        client.save()
        cont +=1
    logging.info(f"Valores actualizados: {cont}")



def for_refresh(obj_with_vencidas):
    installments = obj_with_vencidas.exclude(condition__in=['Pagada', 'Refinanciada']).filter(end_date__date__lt=date.today())

    for installment_ven in installments:
        if isinstance(installment_ven, Installment):
            credit = installment_ven.credit
            client = credit.client
            if not installment_ven.is_refinancing_installment:
                installment_ven.condition = 'Vencida'
        elif isinstance(installment_ven, InstallmentRefinancing):
            credit = installment_ven.refinancing.credit
            client = credit.client
            installment_ven.condition = 'Vencida'
        else:
            print(f"installment_ven type: {type(installment_ven)}")
            credit = installment_ven.refinancing.installment_ref.last().credit
            client = credit.client
            installment_ven.condition = 'Vencida'

        installment_ven.is_caduced_installment = True

        if (installment_ven.start_date.date() + relativedelta(months=1)) < installment_ven.end_date.date():
            new_end_date = datetime.combine(installment_ven.lastup, installment_ven.end_date.time())
            installment_ven.end_date = new_end_date

        resto = abs((date.today() - installment_ven.lastup).days)
        actualice(resto, installment_ven)
        installment_ven.lastup = date.today()
        installment_ven.save()

        daily_interest = installment_ven.porcentage_daily_interests

        if isinstance(credit, Credit):
            new_score = max(0, min(client.score - daily_interest * resto, 1500))
            client.score = new_score
        else:
            new_score = max(0, min(client.score - daily_interest * resto, 1500))
            client.score = new_score

        client.save()


def actualice(resto, installment_ven):
    daily_interes = (resto * installment_ven.original_amount * installment_ven.porcentage_daily_interests / 100)
    installment_ven.daily_interests += daily_interes
    installment_ven.amount = round_to_nearest_hundred(installment_ven.original_amount + installment_ven.daily_interests)


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

                credit.payment_date = credit.installments.last().payment_date
                credit.is_paid = True
                credit.save()

def search_client(request):
    search_terms = request.GET.get('search_term').split()
    clients=Client.objects.all()
    if search_terms:
        for term in search_terms:
            q_objects = Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(dni__icontains=term)
            clients = clients.filter(q_objects)

        data = {
            'clientes': [
                {
                    'id': client.id,
                    'full_name': f'{client.first_name} {client.last_name}',
                    'dni': client.dni,
                } for client in clients
            ]
        }
    else:
        data = {'clientes': []}

    return JsonResponse(data)


def search_credit(request):
    search_terms = request.GET.get('search_term').split()

    credits=Credit.objects.filter(guarantor__isnull=True)
    if search_terms:
        for term in search_terms:
            q_objects = Q(client__first_name__icontains=term) | Q(client__last_name__icontains=term) | Q(client__dni__icontains=term)
            credits = credits.filter(q_objects)

        data = {
            'credits': [
                {
                    'id': credit.id,
                    'full_name': f'{credit.detail_str()}',
                } for credit in credits
            ]
        }
    else:
        data = {'credits': []}

    return JsonResponse(data)


def ask_is_old(credit, adviser):
    credit.amount = round_to_nearest_hundred(credit.amount)
    if not credit.is_old_credit:
        credit.mov = create_movement(credit, adviser)
    credit.is_old_credit = False
    credit.save()