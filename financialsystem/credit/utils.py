from datetime import date
from dateutil.relativedelta import relativedelta

from django.http import JsonResponse

from core.utils import round_to_nearest_special, round_to_nearest_hundred
from cashregister.utils import create_movement
from .models import Credit, Refinancing, Installment
from clients.models import Client

from django.db.models import Q


def all_properties_credit():
        return ["Monto solicitado", "Monto a devolver", "Numero de cuotas", "Monto de las cuotas", "Estado", "Cliente", "Asesor", "Fecha de registro", "Fecha de Finalizacion"]


def refresh_condition():
    if Credit.objects.exists():
        credits_ok = Credit.objects.filter(condition='A Tiempo')
        cred_with_vencidas = credits_ok.filter(installments__end_date__date__lt=date.today())
        refinances = Refinancing.objects.filter(installments__end_date__lt=date.today())
        print(cred_with_vencidas)

        mi_lista = [cred_with_vencidas, refinances] if cred_with_vencidas and refinances else [cred_with_vencidas] if cred_with_vencidas else [refinances] if refinances else []
    
        for model in mi_lista:
            for obj_with_vencidas in model:
                for_refresh(obj_with_vencidas.installments.all())

        for credit in credits_ok:
            if credit.installments.filter(condition="Vencida").count() == credit.installments.count():
                credit.condition = "Vencido"
                credit.is_paid = False
                credit.save()

        refresh_installments_credits()


def for_refresh(obj_with_vencidas):
    installments = obj_with_vencidas.filter(end_date__date__lt=date.today()).exclude(condition = 'Pagada')
    for installment_ven in installments:
        if isinstance(installment_ven, Installment):
            credit = installment_ven.credit
            client = credit.client
            if not installment_ven.is_refinancing_installment:
                installment_ven.condition = 'Vencida'
        else:
            credit = installment_ven.refinancing.installment_ref.last().credit
            client = credit.client
            installment_ven.condition = 'Vencida' 

        installment_ven.is_caduced_installment = True
        resto = abs((date.today() - installment_ven.end_date.date()).days)
        if (installment_ven.start_date.date() + relativedelta(months=1)) < installment_ven.end_date.date():
            print('############# TERMINA EL PLAZO')
            # fifteen_later = installment_ven.end_date - timedelta(days=15)
            installment_ven.end_date = installment_ven.lastup

        actualice(resto, installment_ven)
        installment_ven.save()

        daily_interest = installment_ven.porcentage_daily_interests

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


def actualice(resto, installment_ven):
    daily_interes = round_to_nearest_special((resto * installment_ven.original_amount * installment_ven.porcentage_daily_interests/100))
    installment_ven.daily_interests = daily_interes
    installment_ven.amount = installment_ven.original_amount + daily_interes
    installment_ven.amount = round_to_nearest_hundred(installment_ven.amount)


def refresh_installments_credits():
    for model in [Refinancing, Credit]:
        credits_WPI = model.objects.filter(installments__condition='Pagada')
        for credit in credits_WPI: # WPI = With Paid Installments
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