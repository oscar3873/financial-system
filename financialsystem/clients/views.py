from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from .utils import all_properties_client, all_properties_client_quot
from credit.utils import actualizar_fechas, total_to_ref


from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

#CRUD CLIENT
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from django.urls import reverse_lazy
#FORMS
from clients.forms import ClientForm, PhoneNumberFormSet, CreditForm, CreditFormSet
#MODEL
from .models import Client, PhoneNumber
from credit.models import Credit

# Create your views here.


#CREACION DE UN CREDITO
#------------------------------------------------------------------
class CreditCreate(CreateView):
    form_class = CreditForm
    model = Credit
    template_name = 'form/form.html'

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
    
#DETALLE DE CLIENTE
#------------------------------------------------------------------
class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["credits"] = Credit.objects.all().filter(client = context["client"])
        if context["credits"]:
            context["credit_active"] = Credit.objects.filter(client = context["client"]).filter(condition = 'A Tiempo').last()
            context["installments"] = context["credit_active"].installment.all()
        return context

    def get_object(self):
        return get_object_or_404(Client, id=self.kwargs['pk'])

#CLASE PARA NO REPETIR CODIGO
#------------------------------------------------------------------
class ClientInline(LoginRequiredMixin):
    #ASOCIACION DEL FORMULARIO
    form_class = ClientForm
    model = Client
    template_name = 'clients/client_form.html'
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    
    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))
        self.object = form.save()
        self.object.adviser = self.request.user
        self.object.save()
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return super().form_valid(form)
    
    def formset_phone_numbers_valid(self, formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        phone_numbers = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for phone_number in phone_numbers:
            phone_number.client = self.object
            phone_number.save()

    def formset_credit_valid(self, formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        credits = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for credit in credits:
            credit.client = self.object
            credit.save()


#CREACION DE UN CLIENTE
#------------------------------------------------------------------
class ClientCreate(ClientInline, CreateView):    
    
    def get_context_data(self, **kwargs):
        ctx = super(ClientCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
    
    def get_success_url(self) -> str:
        messages.success(
            self.request, 
            'El cliente dado de alta correctamente', 
            "success")
        return  reverse_lazy('clients:list')
    
    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'credit': CreditFormSet(prefix='credit'),
                'phone_numbers': PhoneNumberFormSet(prefix='phone_numbers'),
            }
        else:
            return {
                'credit': CreditFormSet(self.request.POST or None, self.request.FILES or None, prefix='credit'),
                'phone_numbers': PhoneNumberFormSet(self.request.POST or None, self.request.FILES or None, prefix='phone_numbers'),
            }

#ACTUALIZACION DE UN CLIENTE
#------------------------------------------------------------------
class ClientUpdate(ClientInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(ClientUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        print(ctx)
        return ctx
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Los datos de modificado satisfactoriamente', "info")
        return  reverse_lazy('clients:list')

    def get_named_formsets(self):
        return {
            'phone_numbers': PhoneNumberFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='phone_numbers'),
        }
        
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
    template_name = 'clients/query.html'
    model = Client
    
    def get(self, request, *args, **kwargs):
        found = self.request.GET.get("search")
        if found != None and found != '':
            search = self.model.objects.filter(
                Q(dni__iexact = self.request.GET.get("search"))
                )
            if search.count() > 0:
               return redirect('clients:detail', pk=search.last().pk)
            else:
                self.extra_context = {"found": False}
        return super().get(request, *args, **kwargs)