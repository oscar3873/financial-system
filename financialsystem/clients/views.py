from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

#CRUD CLIENT
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from django.urls import reverse_lazy
#FORMS
from clients.forms import ClientForm, PhoneNumberFormSet
#MODEL
from .models import Client, PhoneNumber
# Create your views here.

#LISTA DE CLIENTES
#------------------------------------------------------------------
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    ordering = ['created_at']
    paginate_by = 2
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["count_clients"] = self.model.objects.all().count()
        context["clients"] = self.model.objects.all()
        #VALIDACION DE EXISTENCIA PARA AL MENOS UN CLIENTE
        if self.model.objects.all().count() > 0:
            context["properties"] = self.model.objects.all()[0].all_properties()
        
        return context
    
#DETALLE DE CLIENTE
#------------------------------------------------------------------
class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        print(context)
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
    
    def get_form_kwargs(self):
        
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))
        self.object = form.save()
        
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

#CREACION DE UN CLIENTE
#------------------------------------------------------------------
class ClientCreate(ClientInline, CreateView):    
    
    def get_context_data(self, **kwargs):
        ctx = super(ClientCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Cliente dado de alta correctamente', "success")
        return  reverse_lazy('clients:list')
    
    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'phone_numbers': PhoneNumberFormSet(prefix='phone_numbers'),
            }
        else:
            return {
                'phone_numbers': PhoneNumberFormSet(self.request.POST or None, self.request.FILES or None, prefix='phone_numbers'),
            }

#ACTUALIZACION DE UN CLIENTE
#------------------------------------------------------------------
class ClientUpdate(ClientInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(ClientUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Cliente modificado satisfactoriamente', "info")
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