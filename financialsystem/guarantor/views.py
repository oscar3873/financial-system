from datetime import datetime
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from babel.dates import format_date
from django.shortcuts import get_object_or_404, redirect

from django.urls import reverse_lazy

#CRUD Guarantor
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from credit.utils import refresh_condition
from cashregister.utils import create_cashregister
from .models import Guarantor
from .forms import GuarantorForm, GuarantorUpdateForm
from .filters import ListingFilter

# Create your views here.
class GuarantorListView(LoginRequiredMixin, ListView):
    """
    Lista de clientes con autenticacion de logeo.
    """
    model = Guarantor
    template_name = 'guarantor/guarantor_list.html'
    ordering = ['-created_at']
    paginate_by = 4
    filter_class = ListingFilter
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('guarantors:list')   
    
    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los clientes que se encuentran en la base de datos para usarlo en el contexto.
        """
        refresh_condition()
        create_cashregister()
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        
        # Etiqueta para el día actual
        today = timezone.now().date()

        # Etiqueta para el mes actual
        month = datetime.today().month
        label_month = format_date(timezone.now(), format='MMMM Y', locale='es').capitalize()
        label_day = f'Hoy {timezone.now().date().day} de {label_month}'
        year = timezone.now().year
        label_year = str(year)
        label_historial = "Historico"
        # Cantidad de clientes histórica
        count_guarantors = self.model.objects.count()
        count_guarantors_today = self.model.objects.filter(created_at__date=today).count()
        count_guarantors_this_month = self.model.objects.filter(created_at__year=year, created_at__month=month).count()
        count_guarantors_this_year = self.model.objects.filter(created_at__year=year).count()
        count_guarantors_dict = [
            {'label':label_historial, 'value':count_guarantors},
            {'label':label_day, 'value':count_guarantors_today},
            {'label':label_month, 'value':count_guarantors_this_month},
            {'label':label_year, 'value':count_guarantors_this_year},
        ]
        # Contextos
        context["count_guarantors_dict"] = count_guarantors_dict
        context["guarantors"] = self.model.objects.all()
        context["listing_filter"] = ListingFilter(self.request.GET, context['guarantors'])
        return context
    
    def get_queryset(self):
        """
        Retorna un queryset de objetos que serán utilizados para renderizar la vista.
        """
        queryset = super().get_queryset()
        return ListingFilter(self.request.GET, queryset=queryset).qs


class GuarantorDetailView(LoginRequiredMixin, DetailView):
    """
    Detalle de un garante.
    """
    model = Guarantor
    template_name = "guarantor/guarantor_detail.html"
    
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('guarantors:list')
           
    def get_object(self):
        """
        Retorna un objeto que será utilizado para renderizar la vista.
        """	
        refresh_condition()
        return get_object_or_404(Guarantor, id=self.kwargs['pk'])

#CREACION DE UNA NOTA
class GuarantorCreateView(CreateView):
    """
    Crea un nuevo garante.
    """
    model = Guarantor
    form_class = GuarantorForm
    template_name = "guarantor/guarantor_form.html"

    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('guarantors:list')
           
    def get_success_url(self) -> str:
        """
        Redirecciona al listado de garantes, con un mensaje de creacion exitosa.
        """
        messages.success(self.request, 'Garante creada correctamente', "success")
        return  reverse_lazy('guarantors:list')

#BORRADO DE UNA NOTA
#------------------------------------------------------------------
class GuarantorDeleteView(DeleteView):
    """
    Borra un garante.
    """
    model = Guarantor

    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('guarantors:list')
           
    def get_success_url(self) -> str:
        """
        Redirecciona al listado de garantes, con un mensaje de eliminacion exitosa.
        """
        messages.success(self.request, 'Garante eliminada correctamente', "danger")
        return  reverse_lazy('guarantors:list')

#ACTUALIZACION DE UN MOVIMIENTO
#------------------------------------------------------------------
class GuarantorUpdateView(UpdateView):
    """
    Actualiza un garante.
    """	
    model = Guarantor
    form_class = GuarantorUpdateForm
    template_name_suffix = '_update_form'

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('guarantors:list')
        
    def form_invalid(self, form):
        """
        Devuelve los datos preciamente ingresados, cuando el formulario es invalido.
        """        
        form.data = form.data.copy()
        form.data['guarantor-dni'] = self.object.dni
        form.data['guarantor-email'] = self.object.email

        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self) -> str:
        """
        Redirecciona al listado de garantes, con un mensaje de actualizacion exitosa.
        """	
        messages.success(self.request, 'Garante actualizada satisfactoriamente', "info")
        return  reverse_lazy('guarantors:list')