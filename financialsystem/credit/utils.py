from datetime import date
from decimal import Decimal

from django.http import JsonResponse

from commissions.models import Interest
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
                installment_ven.condition = 'Vencida'
        else:
            client = installment_ven.refinancing.installment_ref.last().credit.client
            installment_ven.condition = 'Vencida' 

        installment_ven.is_caduced_installment = True

        if installment_ven.lastup != date.today():
            dates = installment_ven.lastup

        elif installment_ven.daily_interests == 0:
            dates = installment_ven.end_date.date()

        else:
            dates = date.today()

        resto = abs((date.today() - dates).days)
        client.score -= Interest.objects.first().daily_interest*resto
        installment_ven.daily_interests += resto * installment_ven.amount * Decimal(Interest.objects.first().daily_interest/100)
        installment_ven.lastup = date.today()
        installment_ven.save()
        client.save()


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
                        credit.is_paid = True
                        credit.payment_date = credit.installments.last().payment_date

                credit.is_paid = True
                credit.save()

    

def search_client(request):
    search_terms = request.GET.get('search_term').split()
    clients=Client.objects.all()
    if search_terms:
        # Separar el término de búsqueda en palabras
        for term in search_terms:
            q_objects = Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(dni__icontains=term)
            clients = clients.filter(q_objects)
        
        # Serializar los resultados como un diccionario de Python
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
    print(search_terms)
    credits=Credit.objects.all()
    if search_terms:
        # Separar el término de búsqueda en palabras
        for term in search_terms:
            q_objects = Q(client__first_name__icontains=term) | Q(client__last_name__icontains=term) | Q(client__dni__icontains=term)
            credits = credits.filter(q_objects)
        
        print(credits)
        # Serializar los resultados como un diccionario de Python
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