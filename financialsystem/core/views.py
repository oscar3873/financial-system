import itertools
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from credit.models import Credit, Installment, InstallmentRefinancing, Refinancing
from clients.models import Client


from note.models import Note
from cashregister.models import CashRegister, Movement
from cashregister.utils import create_cashregister

# Create your views here.

class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"
    modelNote = Note
    modelCashregister = CashRegister
    modelMovement = Movement
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    

    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los modelos necesarios que se encuentran en la base de datos para usarlo en el contexto.
        """
        create_cashregister()
        context = super().get_context_data(**kwargs)
        Caja = CashRegister.objects.get_or_create()
        context["cashregister"] = Caja[0]
        context["notes"] = Note.objects.all().order_by("-created_at")[0:3]
        context["movements"] = Movement.objects.all().order_by("-created_at")[0:3]
        

        try:
             #contexto para visualizar proximos 3 vencimientos para admin o asesor
            if self.request.user.is_superuser:
                clients = Client.objects.all()[0:3]
                credits = Credit.objects.all()[0:3]
                installments = Installment.objects.exclude(condition__in=['Pagada']).exclude(is_refinancing_installment=True).order_by("end_date")
                installments_ref = InstallmentRefinancing.objects.exclude(condition__in=['Pagada']).order_by("end_date")
            else:
                clients = Client.objects.filter(adviser = self.request.user.adviser)
                credits = Credit.objects.filter(client__in=clients)
                installments = Installment.objects.filter(credit__in=credits)      
                refinancings = Refinancing.objects.filter(installment_ref__in=installments)
                #Excluimos ahora si las cuotas refinanciadas porque sino me va mostrar una cuota refinanciada 
                installments = installments.exclude(condition__in=['Pagada']).exclude(is_refinancing_installment=True).order_by("end_date")
                installments_ref = InstallmentRefinancing.objects.filter(refinancing__in=refinancings)
            
            # Concatenamos las dos listas en una sola
            all_installments = list(itertools.chain(installments, installments_ref))
            # Ordenamos la lista resultante por la fecha de vencimiento
            all_installments = sorted(all_installments, key=lambda x: x.end_date)[0:3]
        except:
            clients = []
            credits = []
            all_installments = []
        context["clients"] = clients
        context["credits"] = credits
        context["next_expirations"] = all_installments 
        
        return context