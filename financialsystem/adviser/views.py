from datetime import datetime
from decimal import Decimal
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash

from braces.views import GroupRequiredMixin

from credit.utils import refresh_condition
from cashregister.utils import create_cashregister
from commissions.forms import SettingsInterestForm
from .models import Adviser
from commissions.models import Commission
from .utils import *
from .forms import *

# Create your views here.
class AdviserListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    '''
    Vista de lista de objetos del modelo Adviser, que requiere autenticación y pertenecer al grupo 'admin_group' para acceder a ella.
    '''
    model = Adviser
    group_required = 'admin_group'
    ordering = ['-created_at']
    paginate_by = 4
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    

    def handle_no_permission(self):
        '''
        Redirecciona al usuario a la página de inicio de sesión si no tiene permiso para acceder a la vista.
        '''
        return redirect("/accounts/login/")
    
    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los asesores que se encuentran en la base de datos para usarlo en el contexto.
        """
        refresh_condition()
        create_cashregister()
        context = super().get_context_data(**kwargs)

        context["settings_form"] = SettingsInterestForm(instance = Interest.objects.first()) # CONTEXT DEL FORMULARIO DE SETTINGS

        context["count_advisers"] = Adviser.objects.count()
        context["advisers"] = Adviser.objects.all()
        return context

    

class AdviserDetailView(LoginRequiredMixin, DetailView):
    """
    Vista para ver los detalles de un asesor.
    """
    model = Adviser
    group_required = 'admin_group'
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def handle_no_permission(self, request):
        """
        Redirige al usuario a la página de inicio si no tiene permisos para ver la vista.
        """
        return redirect("/")

    
    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los asesores que se encuentran en la base de datos para usarlo en el contexto.
        """
        refresh_condition()
        context = super().get_context_data(**kwargs)
        context["settings_form"] = SettingsInterestForm(instance = Interest.objects.first())
        context["commissions"] = Commission.objects.filter(adviser=self.get_object(), is_paid=False)
        context["properties"] = commission_properties()
        return context


#----------------------------------------------------------------
def is_admin(user):
    if user.is_superuser:
        return user.is_superuser
    else:
        messages.error('Lo sentimos, no tienes aceso a este apartado')
        return False

@login_required(login_url="/accounts/login/")
@user_passes_test(is_admin)
def pay_commission(request, pk):
    '''Función que maneja la vista para pagar una comisión'''

    refresh_condition()

    try:
        commission = Commission.objects.get(id=pk)
    except Commission.DoesNotExist:
        return redirect('advisers:detail', pk=commission.adviser.id)

    if commission.is_paid:
        messages.error(request, "Esta comisión ya ha sido pagada.")
        return redirect('advisers:detail', pk=commission.adviser.id)

    commission.is_paid = True
    porcentage_value = Decimal(request.POST.get('porcentage'))
    real_value = Decimal(round((commission.amount*100)/commission.interest))  # Calculo para saber el monto original (el 100%)
    
    commission.amount = Decimal(real_value*(porcentage_value/100)) # Monto de la comision   
    commission.operation_amount = real_value 
    commission.interest = Decimal(porcentage_value)
    commission.last_up = datetime.now()
    
    commission.save()

    messages.success(request, "La comisión se ha pagado exitosamente.")
    request.session['success_message'] = "La comisión se ha pagado exitosamente." # almacenar mensaje en la sesión
    return redirect('advisers:detail', pk=commission.adviser.id)

class AdviserUpdateView(UpdateView):
    model = Adviser
    fields = ["avatar"]
    template_name = "adviser/adviser_update_form.html"

    def get_success_url(self) -> str:
        return reverse('advisers:detail', args=[self.kwargs["pk"]])
    
class AdviserDeleteView(DeleteView):
    pass


