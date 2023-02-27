from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from .utils import all_properties_client


from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

#CRUD CLIENT
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView

from django.urls import reverse_lazy
#FORMS
from .forms import ClientForm
#MODEL
from .models import Client, PhoneNumber
from credit.models import Credit

# Create your views here.

#LISTA DE CLIENTES
#------------------------------------------------------------------
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    ordering = ['-created_at']
    paginate_by = 4
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_context_data(self, **kwargs):
        # actualizar_fechas()
        context = super().get_context_data(**kwargs)
        context["count_clients"] = self.model.objects.all().count()
        context["clients"] = self.model.objects.all()
        context["properties"] = all_properties_client()
        if self.request.GET.get("search") != None:
            search = Client.objects.filter(
                Q(first_name__icontains = self.request.GET.get("search")) |
                Q(last_name__icontains = self.request.GET.get("search")) |
                Q(civil_status__icontains = self.request.GET.get("search")) |
                Q(dni__icontains = self.request.GET.get("search"))
                )
            context["clients"] = search
        return context
    

#CREACION DE UN CLIENTE
#------------------------------------------------------------------
class ClientCreate(LoginRequiredMixin, CreateView):    
    form_class = ClientForm
    model = Client
    template_name = 'clients/client_form.html'
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    
    def get_success_url(self) -> str:
        messages.success(
            self.request, 
            'El cliente dado de alta correctamente', 
            "success")
        return  reverse_lazy('clients:list')

#ACTUALIZACION DE UN CLIENTE
#------------------------------------------------------------------
class ClientUpdate(LoginRequiredMixin, UpdateView):
    form_class = ClientForm
    model = Client
    template_name = 'clients/client_update_form.html'
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    

    def get_success_url(self) -> str:
        messages.success(self.request, 'Los datos de modificado satisfactoriamente', "info")
        return  reverse_lazy('clients:list')
        
#BORRADO DE NUMEROS DE UN CLIENTE
#------------------------------------------------------------------
def delete_phone_number(request, pk):
    try:
        phone_number = PhoneNumber.objects.get(id=pk)
    except PhoneNumber.DoesNotExist:
        return redirect('clients:update', pk=phone_number.client.id)
    phone_number.delete()
    return redirect('clients:update', pk=phone_number.client.id)

#BORRADO DE UN CLIENTE
#------------------------------------------------------------------
class ClientDelete(DeleteView):
    model = Client
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Cliente eliminado correctamente', "danger")
        return  reverse_lazy('clients:list')

#CONSULTA
#------------------------------------------------------------------
class QueryView(ListView):
    template_name = 'clients/query/query.html'
    model = Client
    
    def get(self, request, *args, **kwargs):
        found = self.request.GET.get("search")
        if found != None and found != '':
            try: 
                search = self.model.objects.get(dni=found)
                return redirect('clients:detail', pk=search.pk)
            except :
               self.extra_context = {"found": False}
                
        return super().get(request, *args, **kwargs)

#DETALLE DE CLIENTE
#------------------------------------------------------------------
class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["credits"] = Credit.objects.filter(client = context["client"])
        if context["credits"]:
            context["credit_active"] = Credit.objects.filter(client = context["client"]).filter(condition = 'A Tiempo').last()
            context["installments"] = context["credit_active"].installment.all()
        return context

    def get_object(self):
        return get_object_or_404(Client, id=self.kwargs['pk'])