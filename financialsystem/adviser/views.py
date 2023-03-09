from decimal import Decimal
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test


from braces.views import GroupRequiredMixin

from credit.utils import refresh_condition
from .models import Adviser, Comission
from .utils import commission_properties
from cashregister.models import CashRegister, Movement

# Create your views here.
class AdviserListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    '''
    Vista de lista de objetos del modelo Adviser, que requiere autenticación y pertenecer al grupo 'admin_group' para acceder a ella.
    '''
    model = Adviser
    group_required = 'admin_group'
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
        context = super().get_context_data(**kwargs)
        context["count_advisers"] = Adviser.objects.count()
        context["advisers"] = Adviser.objects.all()
        return context

    

class AdviserDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
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
        context["commissions"] = Comission.objects.filter(adviser=self.get_object(), is_paid=False)
        context["properties"] = commission_properties()
        return context

    def get_object(self):
        """
        Devuelve el objeto asesor correspondiente al id pasado como parámetro en la url.
        """
        try:
            adviser = Adviser.objects.get(id=self.kwargs["pk"])
            return adviser
        except Adviser.DoesNotExist:
            raise Http404


#----------------------------------------------------------------
def is_admin(user):
    return user.is_superuser

@login_required(login_url="/accounts/login/")
@user_passes_test(is_admin)
def pay_commission(request, pk):
    '''Función que maneja la vista para pagar una comisión'''

    refresh_condition()

    try:
        commission = Comission.objects.get(id=pk)
    except Comission.DoesNotExist:
        return redirect('advisers:detail', pk=commission.adviser.id)

    if commission.is_paid:
        messages.error(request, "Esta comisión ya ha sido pagada.")
        return redirect('advisers:detail', pk=commission.adviser.id)

    commission.is_paid = True
    porcentage_value = request.POST.get('porcentage')
    print(porcentage_value)
    commission._last_interest = Decimal(porcentage_value) # Agrego un atributo privado para utilizarlo unica vez en la señal de Commission
    # commission.save()
    # create_movement(commission)

    messages.success(request, "La comisión se ha pagado exitosamente.")
    return redirect('advisers:detail', pk=commission.adviser.id)


class AdviserUpdateView(UpdateView):
    model = Adviser
    

class AdviserDeleteView(DeleteView):
    pass


def create_movement(commission):
    '''Crea un nuevo objeto Movement y lo guarda en la base de datos.'''
    mov = Movement.objects.create(
            user = commission.adviser,
            amount = commission.amount,
            cashregister = CashRegister.objects.last(),
            operation_mode = 'EGRESO',
            description = 'COMISION %s - %s' % (commission.adviser, commission.type),
            money_type= commission.money_type
        )
    commission.id_mov = mov.id
    commission.save()