from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from credit.utils import refresh_condition
from .utils import all_properties_mov
from .tables import MovementTable

from babel.dates import format_date

from django import forms

from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

from django.urls import reverse_lazy

#CRUD MOVEMENT
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from .models import Movement, CashRegister
from .forms import MovementForm, MovementUpdateForm
from django.views.generic.edit import FormView

from .filters import DescriptionFilter, ListingFilter, MoneyTypeFilter, AmountFilter, UserFilter

from django.db.models import Sum
from django.utils import timezone

# Create your views here.
class CashRegisterListView(LoginRequiredMixin, FormView, ListView):
    '''
    Vista general de CashRegister, con autenticación de usuario logeado, con filtrado para los campos de Movement.
    '''
    model = Movement
    second_model = CashRegister 
    form_class = MovementForm
    template_name = 'cashregister/cashregister.html'
    filter_class = ListingFilter
    paginate_by = 5
    ordering = ['-created_at']
    
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_context_data(self, **kwargs):
        """
        Extrae los datos de la caja que se encuentran en la base de datos para usarlo en el contexto.
        """
        refresh_condition()
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        
        if not CashRegister.objects.exists():
            CashRegister.objects.create()
    
        # Etiqueta para el día actual
        today = timezone.now().date()

        # Etiqueta para el mes actual
        month = datetime.today().month
        label_month = format_date(timezone.now(), format='MMMM Y', locale='es').capitalize()
        label_day = f'Hoy {timezone.now().date().day} de {label_month}'

        # Etiqueta para el año actual
        year = timezone.now().year
        label_year = str(year)

        balances = [
            {'money_type':'ARS','label': label_day, 'value': Movement.objects.filter(money_type="PESOS").filter(created_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'ARS','label': label_month, 'value': Movement.objects.filter(money_type="PESOS").filter(created_at__year=year, created_at__month=month).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'ARS','label': label_year, 'value': Movement.objects.filter(money_type="PESOS").filter(created_at__year=year).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'USD','label': label_day, 'value': Movement.objects.filter(money_type="USD").filter(created_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'USD','label': label_month, 'value': Movement.objects.filter(money_type="USD").filter(created_at__year=year, created_at__month=month).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'USD','label': label_year, 'value': Movement.objects.filter(money_type="USD").filter(created_at__year=year).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'TRANSFER','label': label_day, 'value': Movement.objects.filter(money_type="TRANSFER").filter(created_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'TRANSFER','label': label_month, 'value': Movement.objects.filter(money_type="TRANSFER").filter(created_at__year=year, created_at__month=month).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'TRANSFER','label': label_year, 'value': Movement.objects.filter(money_type="TRANSFER").filter(created_at__year=year).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'CREDITO','label': label_day, 'value': Movement.objects.filter(money_type="CREDITO").filter(created_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'CREDITO','label': label_month, 'value': Movement.objects.filter(money_type="CREDITO").filter(created_at__year=year, created_at__month=month).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'CREDITO','label': label_year, 'value': Movement.objects.filter(money_type="CREDITO").filter(created_at__year=year).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'DEBITO','label': label_day, 'value': Movement.objects.filter(money_type="DEBITO").filter(created_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'DEBITO','label': label_month, 'value': Movement.objects.filter(money_type="DEBITO").filter(created_at__year=year, created_at__month=month).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'DEBITO','label': label_year, 'value': Movement.objects.filter(money_type="DEBITO").filter(created_at__year=year).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'EUR','label': label_day, 'value': Movement.objects.filter(money_type="EUR").filter(created_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'EUR','label': label_month, 'value': Movement.objects.filter(money_type="EUR").filter(created_at__year=year, created_at__month=month).aggregate(Sum('amount'))['amount__sum'] or 0},
            {'money_type':'EUR','label': label_year, 'value': Movement.objects.filter(money_type="EUR").filter(created_at__year=year).aggregate(Sum('amount'))['amount__sum'] or 0},
        ]
        context["balances"] = balances
    
        context["cashregister"] = CashRegister.objects.last()
        context["lastmovements"] = self.model.objects.all()[:4]
        context["count_movements"] = self.model.objects.all().count()
        context["movements"] = self.model.objects.all()
        context["properties"] = all_properties_mov()
        
        context["listing_filter"] = ListingFilter(self.request.GET, context['movements'])
        context['listing_filter'] = self.filterset
        context['listing_filter_params'] = self.request.GET.urlencode()
        return context
    
    def form_valid(self, form):
        """
        Función que se encarga de guardar el formulario.
        """
        user = self.request.user
        movement = form.save(commit=False)
        movement.user = user.adviser  # Establecer el usuario actual
        movement.cashregister = CashRegister.objects.last()
        movement.save()
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Muestra la causa por el cual el formulario no es válido.
        """	
        raise Exception("El formulario no es válido: {}".format(form.errors))

    def get_form_kwargs(self):
        """
        Función que se encarga de obtener los parámetros del formulario.
        """
        kwargs = super(CashRegisterListView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
        #DEFINICION DEL TIPO DE FILTRO ULTILIZADO
    def get_queryset(self):
        """
        Retorna un queryset de objetos que serán utilizados para renderizar la vista.
        """
        queryset = super().get_queryset()
        self.filterset = self.filter_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.order_by(*self.ordering)
    
    def get_success_url(self) -> str:
        """
        Método que redirige al usuario a la página de inicio después de crear un nuevo movimiento.
        """
        return reverse_lazy('cashregister:home')

#LISTA DE MOVIMIENTOS
#----------------------------------------------------------------
class MovementListView(LoginRequiredMixin, ListView, MovementTable):
    """
    Vista basada en clase para mostrar una lista de movimientos de caja.
    """
    model = Movement
    template_name = "cashregister/movement_list.html"
    paginate_by = 20
    ordering = ['-created_at']
    
    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los movimientos que se encuentran en la base de datos para usarlo en el contexto.
        """
        refresh_condition()
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context["count_movements"] = self.model.objects.all().count()
        context["movements"] = self.model.objects.all()
        context["listing_filter"] = ListingFilter(self.request.GET, context['movements'])
        context["money_filter"] = MoneyTypeFilter(self.request.GET, context['movements'])
        context["amount_filter"] = AmountFilter(self.request.GET, context['movements'])
        context["description_filter"] = DescriptionFilter(self.request.GET, context['movements'])
        context["user_filter"] = UserFilter(self.request.GET, context['movements'])
        context["properties"] = all_properties_mov()

        return context
    
    #DEFINICION DEL TIPO DE FILTRO ULTILIZADO
    def get_queryset(self):
        """
        Devuelve el conjunto de consultas para la lista de movimientos.
        """
        queryset = super().get_queryset()
        if "user" in self.request.GET and len(self.request.GET) == 1:
            return UserFilter(self.request.GET, queryset=queryset).qs
        elif ("amount_min" or "amount_max") in self.request.GET :
            return AmountFilter(self.request.GET, queryset=queryset).qs
        elif "money_type" in self.request.GET and len(self.request.GET) == 1:
            return MoneyTypeFilter(self.request.GET, queryset=queryset).qs
        elif "description" in self.request.GET and len(self.request.GET) == 1:
            return DescriptionFilter(self.request.GET, queryset=queryset).qs
        else:
            return ListingFilter(self.request.GET, queryset=queryset).qs


class MovementDetailView(LoginRequiredMixin, DetailView):
    """
    Vista de detalle de un objeto de Movimiento.
    """
    model = Movement
    template_name = 'cashregister/movement_detail.html'
    
    # Se especifica la URL de inicio de sesión y el campo de redirección
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_object(self):
        """
        Obtiene el objeto Movimiento correspondiente al ID dado.
        """
        refresh_condition()  # Actualiza las condiciones de la aplicación
        return get_object_or_404(Movement, id=self.kwargs['pk'])


#BORRADO DE UN MOVIMIENTO
#------------------------------------------------------------------
class MovementDeleteView(DeleteView):
    """
    Clase para eliminar un objeto Movement de la base de datos.
    """
    model = Movement
    
    def get_success_url(self) -> str:
        """
        Obtiene la URL de redirección después de que se ha eliminado correctamente un objeto Movement.
        Agrega un mensaje de éxito a la cola de mensajes.
        """
        messages.success(self.request, '{}, realizada el {}, eliminada satisfactoriamente'.format(self.object, self.object.created_at.date()), "danger")
        return reverse_lazy('cashregister:list')


#ACTUALIZACION DE UN MOVIMIENTO
#------------------------------------------------------------------
class MovementUpdateView(UpdateView):
    """
    Clase para actualizar un objeto Movement de la base de datos.
    """
    model = Movement
    form_class = MovementUpdateForm
    template_name_suffix = '_update_form'

    # Se especifica la URL de inicio de sesión y el campo de redirección
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_form_kwargs(self):
        """
        Función que se encarga de obtener los parámetros del formulario.
        """
        refresh_condition()
        kwargs = super(MovementUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_success_url(self) -> str:
        """
        Obtiene la URL de redirección después de que se ha actualizado correctamente un objeto Movement.
        Agrega un mensaje de éxito a la cola de mensajes.
        """	
        messages.success(self.request, '{}, realizada el {}, actualizada satisfactoriamente'.format(self.object, self.object.created_at.date()), "info")
        return  reverse_lazy('cashregister:home')