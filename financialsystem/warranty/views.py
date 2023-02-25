from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

from django.urls import reverse_lazy

#CRUD Warranty
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from .models import Warranty
from .forms import WarrantyForm
from .filters import ListingFilter
from .utils import all_properties_warranty

# Create your views here.
class WarrantyListView(LoginRequiredMixin, ListView):
    model = Warranty
    template_name = "warranty/warranty_list.html"
    paginate_by = 6
    ordering = ['-created_at']
    
    def get_context_data(self, **kwargs):
        
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context["count_warrantys"] = self.model.objects.all().count()
        context["warrantys"] = self.model.objects.all()
        context["listing_filter"] = ListingFilter(self.request.GET, queryset=context["warrantys"])
        #VALIDACION DE EXISTENCIA PARA AL MENOS UN CLIENTE
        if self.model.objects.all().count() > 0:
            context["properties"] = all_properties_warranty
        
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return ListingFilter(self.request.GET, queryset=queryset).qs


class WarrantyDetailView(LoginRequiredMixin, DetailView):
    model = Warranty
    template_name = "warranty/warranty_detail.html"
    
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_object(self):
        return get_object_or_404(Warranty, id=self.kwargs['pk'])

#CREACION DE UNA NOTA
class WarrantyCreateView(CreateView):
    model = Warranty
    form_class = WarrantyForm
    template_name = "warranty/warranty_form.html"
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Garante creada correctamente', "success")
        return  reverse_lazy('warrantys:list')

#BORRADO DE UNA NOTA
#------------------------------------------------------------------
class WarrantyDeleteView(DeleteView):
    model = Warranty
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Garante eliminada correctamente', "danger")
        return  reverse_lazy('warrantys:list')

#ACTUALIZACION DE UN MOVIMIENTO
#------------------------------------------------------------------
class WarrantyUpdateView(UpdateView):
    model = Warranty
    form_class = WarrantyForm
    template_name_suffix = '_update_form'
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Garante actualizada satisfactoriamente', "info")
        return  reverse_lazy('warrantys:list')