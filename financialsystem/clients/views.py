from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q

from .utils import all_properties_client

from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect


#CRUD CLIENT
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView

from django.urls import reverse_lazy
#FORMS
from .forms import ClientForm, PhoneNumberFormSet
#MODEL
from .models import Client, PhoneNumberClient
from credit.models import Credit
from credit.forms import RefinancingForm

from payment.forms import PaymentForm



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
    

#ACTUALIZACION DE UN CLIENTE
#------------------------------------------------------------------
def client_update(request, pk):
    client = Client.objects.get(id=pk)
    form = ClientForm(request.POST or None, instance=client, is_update=True)

    formset = PhoneNumberFormSet(request.POST or None, instance=client)
    
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('client_detail', client_id=pk)
    else:
        formset = PhoneNumberFormSet(instance=client, queryset=PhoneNumberClient.objects.filter(client=client))
        
    context = {
        'cliente_form': form,
        'formsetPhoneClient': formset,
    }

    return render(request, 'clients/client_update.html', context=context)
#BORRADO DE NUMEROS DE UN CLIENTE
#------------------------------------------------------------------
def delete_phone_number(request, pk):
    try:
        phone_number = PhoneNumberClient.objects.get(id=pk)
    except PhoneNumberClient.DoesNotExist:
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

        credit_active = Credit.objects.filter(client = context["client"]).filter(condition = 'A Tiempo').last()
        
        excludes = ['Refinanciada', 'Pagada']
        installments = credit_active.installment.exclude(condition__in=excludes)

        context["credits"] = Credit.objects.filter(client = context["client"])
        if context["credits"]:
            context["credit_active"] = credit_active
            context["installments"] = context["credit_active"].installment.all()
            context["first_is_paid"] = context["credit_active"].installment.first().is_paid_installment
            if installments :
                context["form_ref"]= RefinancingForm(credit=context["credit_active"])
                context["form_payment"]= PaymentForm(installments=installments)
                context["amount_installment"] = context["credit_active"].installment.first().amount

        return context

    def get_object(self):
        return get_object_or_404(Client, id=self.kwargs['pk'])
    