from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import UpdateView, DeleteView, CreateView

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages
from .utils import actualizar_fechas, all_properties_credit


from .forms import CreditForm

from .models import Credit

#LISTA DE CREDITOS
#------------------------------------------------------------------
class CreditListView(LoginRequiredMixin, ListView):
    model = Credit
    template_name = 'credits/credit_list.html'
    ordering = ['-id']
    paginate_by = 5
    
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_context_data(self, **kwargs):
        # actualizar_fechas()
        context = super().get_context_data(**kwargs)
        context["count_credits"] = self.model.objects.all().count()
        context["credits"] = self.model.objects.all()
        if self.model.objects.all().count() > 0:
            context["properties"] = all_properties_credit()
        
        return context
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["count_credits"] = self.model.objects.all().count()
        context["credits"] = self.model.objects.all()
        context["properties"] = all_properties_credit()
        return context
    
class CreditDetailView(DetailView):
    model = Credit
    template_name = 'credits/credit_detail.html'

    def get_object(self):
        return get_object_or_404(Credit, id=self.kwargs['id'])


#CREACION DE UN CREDITO
#------------------------------------------------------------------     
class CreditCreateView(CreateView):
    model = Credit
    form_class = CreditForm
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Credito creado correctamente', "success")
        return  reverse_lazy('credits:list')

class CreditUpdateView(UpdateView):
    model = Credit
    form_class = CreditForm
    
class CreditDeleteView(DeleteView):
    model = Credit
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Credito borrado correctamente', "danger")
        return  reverse_lazy('credits:list')
    