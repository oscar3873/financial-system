from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .utils import all_properties_credit
from .forms import CreditForm
from .models import Credit
from cashregister.models import CashRegister, Movement
from adviser.models import Comission

from clients.forms import ClientForm, PhoneNumberFormSet
from warranty.forms import WarrantyForm
from guarantor.forms import GuarantorForm, PhoneNumberFormSet as PhoneNumberFormG


#CREAR UN CREDITO CON TODOS LOS FORMULARIOS ANIDADOS
def crear_credito(request):
    client_form = ClientForm()
    credit_form = CreditForm()
    phone_number_form = PhoneNumberFormSet(request.POST or None)
    phone_number_formG = PhoneNumberFormG(request.POST or None)
    warranty_form = WarrantyForm()
    guarantor_form = GuarantorForm()
    
    if request.method == 'POST':
        print("La solicitud contiene................", request.POST)
        client_form = ClientForm(request.POST)
        credit_form = CreditForm(request.POST)
        phone_number_form = PhoneNumberFormSet(request.POST or None)
        phone_number_formG = PhoneNumberFormG(request.POST or None)
        print("Numero de telefono de client", phone_number_form)
        print("Numero de telefono de garante", phone_number_formG)
        warranty_form = WarrantyForm(request.POST)
        guarantor_form = GuarantorForm(request.POST)
        print(client_form.is_valid())
        print(credit_form.is_valid())
        print(warranty_form.is_valid())
        print(guarantor_form.is_valid())
        
        if client_form.is_valid() and credit_form.is_valid() and warranty_form.is_valid() and guarantor_form.is_valid():
            print("Los formularios son validos")
            client = client_form.save(commit=False)
            client.adviser = request.user.adviser
            client = client_form.save()
            
            print(PhoneNumberFormSet)
            phone_numbers = phone_number_form.save(commit=False)
            for phone_number in phone_numbers:
                print(phone_number)
                phone_number.client = client
                phone_number.save()
            phone_number_form.save_m2m()
            
            credit = credit_form.save(commit=False)
            credit.client = client
            if not credit.is_old_credit:
                create_movement(credit, request.user.adviser)
                comission_create(credit, request.user.adviser)
            credit.save()
            
            guarantor = guarantor_form.save(commit=False)
            if guarantor_form.cleaned_data['dni']:
                guarantor.credit = credit
                guarantor.save()
                phone_numbers = phone_number_formG.save(commit=False)
                for phone_number in phone_numbers:
                    phone_number.guarantor = guarantor
                    phone_number.save()
                    
                phone_number_formG.save_m2m()
            else:
                print("No entro amigo..... !!!!!!")
            
            warranty = warranty_form.save(commit=False)
            if warranty_form.cleaned_data['article']:
                warranty.credit = credit
                warranty.save()
        else:
            print(client_form.errors)
    
    context = {
        'cliente_form': client_form,
        'phone_number_form': phone_number_form,
        'phone_number_formG': phone_number_formG,
        'credito_form': credit_form,
        'empeno_form': warranty_form,
        'garante_form': guarantor_form
    }
    
    return render(request, 'credit/create_credit.html', context)
            
def create_movement(instance, adviser):
    Movement.objects.create(
        user = adviser.user,
        amount = instance.amount,
        cashregister = CashRegister.objects.last(),
        operation_mode = 'EGRESO',
        description = 'CREDITO PARA %s \nCUOTAS: %s' % (instance.client, instance.installment_num),
        money_type = 'PESOS',
        )


def comission_create(instance, adviser):
    amount = instance.amount*Decimal(0.075)
    Comission.objects.create(
        adviser = adviser,
        amount = amount,
        type = 'REGISTRO',
        create_date = instance.start_date,
        ) 
    
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
        return get_object_or_404(Credit, pk=self.kwargs['pk'])


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

    def form_valid(self, form):
        if form.is_valid():
            form.instance.mov.amount = form.instance.amount
            form.instance.mov.save()
            form.instance._isup = True
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Credito actualizado correctamente', "success")
        return  reverse_lazy('credits:list')
    
class CreditDeleteView(DeleteView):
    model = Credit
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Credito borrado correctamente', "danger")
        return  reverse_lazy('credits:list')