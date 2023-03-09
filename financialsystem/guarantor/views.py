from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

from django.urls import reverse_lazy

#CRUD Guarantor
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from credit.utils import refresh_condition
from .models import Guarantor
from .forms import GuarantorForm
from .filters import ListingFilter
from .utils import all_properties_guarantor

# Create your views here.
class GuarantorListView(LoginRequiredMixin, ListView):
    """
    Lista de Garantes.
    """
    model = Guarantor
    template_name = "guarantor/guarantor_list.html"
    paginate_by = 6
    ordering = ['-created_at']
    
    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los garantes que se encuentran en la base de datos para usarlo en el contexto.
        """
        refresh_condition()
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context["count_guarantors"] = self.model.objects.all().count()
        context["guarantors"] = self.model.objects.all()
        context["listing_filter"] = ListingFilter(self.request.GET, queryset=context["guarantors"])
        #VALIDACION DE EXISTENCIA PARA AL MENOS UN CLIENTE
        if self.model.objects.all().count() > 0:
            context["properties"] = all_properties_guarantor
        
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
    form_class = GuarantorForm
    template_name_suffix = '_update_form'
    
    def get_success_url(self) -> str:
        """
        Redirecciona al listado de garantes, con un mensaje de actualizacion exitosa.
        """	
        messages.success(self.request, 'Garante actualizada satisfactoriamente', "info")
        return  reverse_lazy('guarantors:list')