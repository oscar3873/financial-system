from datetime import date, datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from babel.dates import format_date
from clients.filters import ListingFilter

from .utils import all_properties_client
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect


#CRUD CLIENT
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView

from django.urls import reverse_lazy
#FORMS
from .forms import ClientForm, PhoneNumberFormSet, PhoneNumberFormSetUpdate
from guarantor.forms import GuarantorForm
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
    filter_class = ListingFilter
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_context_data(self, **kwargs):
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
        count_clients = self.model.objects.count()
        count_clients_today = self.model.objects.filter(created_at__date=today).count()
        count_clients_this_month = self.model.objects.filter(created_at__year=year, created_at__month=month).count()
        count_clients_this_year = self.model.objects.filter(created_at__year=year).count()
        count_clients_dict = [
            {'label':label_historial, 'value':count_clients},
            {'label':label_day, 'value':count_clients_today},
            {'label':label_month, 'value':count_clients_this_month},
            {'label':label_year, 'value':count_clients_this_year},
        ]
        # Contextos
        context["count_clients_dict"] = count_clients_dict
        context["clients"] = self.model.objects.all()
        context["properties"] = all_properties_client()
        context["listing_filter"] = ListingFilter(self.request.GET, context['clients'])
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filter_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.order_by(*self.ordering)
    
    def get_success_url(self) -> str:
        return reverse_lazy('clients:list')
    

#ACTUALIZACION DE UN CLIENTE
#-----------------------------------------------------------------
class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name_suffix = '_update'

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['phone_formset'] = PhoneNumberFormSetUpdate(self.request.POST, instance=self.object)
        else:
            context['phone_formset'] = PhoneNumberFormSetUpdate(instance=self.object)
        return context

    def form_invalid(self, form):
        print("Esto re invalido amigoooo", form.errors)
        return super().form_invalid(form)
    
    def form_valid(self, form):
        print("Estoy aca amigo")
        response = super().form_valid(form)
        phone_formset = PhoneNumberFormSetUpdate(self.request.POST, instance=self.object)
        phone_formset.save()
        
        return response

    def get_success_url(self) -> str:
        messages.success(self.request, '{}, realizada el {}, actualizada satisfactoriamente'.format(self.object, self.object.created_at.date()), "info")
        return reverse_lazy('clients:list')
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
class ClientDelete(LoginRequiredMixin, DeleteView):
    model = Client
    
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Cliente eliminado correctamente', "danger")
        return  reverse_lazy('clients:list')

#CONSULTA
#------------------------------------------------------------------
class QueryView(ListView):
    template_name = 'core/consultas.html'
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
class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
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
    