from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView, CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .utils import *

from .models import Credit, Refinancing, Installment
from clients.models import Client
from guarantor.models import Guarantor

from .forms import CreditForm, RefinancingForm
from guarantor.forms import GuarantorForm, PhoneNumberFormSetG
from warranty.forms import WarrantyForm
from clients.forms import ClientForm, PhoneNumberFormSet

#CREAR UN CREDITO CON TODOS LOS FORMULARIOS ANIDADOS

def crear_credito(request):
    client_form = ClientForm(request.POST or None)
    guarantor_form = GuarantorForm(request.POST or None)
    warranty_form = WarrantyForm(request.POST or None)
    credit_form = CreditForm(request.POST or None)
    formsetPhoneClient = PhoneNumberFormSet(request.POST or None, instance=Client(), prefix = "phone_number_client")
    formsetPhoneGuarantor = PhoneNumberFormSetG(request.POST or None, instance=Guarantor(), prefix = "phone_number_guarantor")
    
    if request.method == 'POST':
        print("La solicitud contiene................", request.POST)        
        if client_form.is_valid() and credit_form.is_valid() and warranty_form.is_valid() and guarantor_form.is_valid() and formsetPhoneClient.is_valid() and formsetPhoneGuarantor.is_valid():
            client = client_form.save(commit=False)
            client.adviser = request.user.adviser
            client.save()
            phone_numbers = formsetPhoneClient.save(commit=False)
            for phone_number in phone_numbers:
                if phone_number.phone_number_c:
                    phone_number.client = client
                    phone_number.save()
                    
            credit = credit_form.save(commit=False)
            credit.client = client
            if not credit.is_old_credit:
                credit.mov = create_movement(credit, request.user.adviser)
            credit.save()
            
            guarantor = guarantor_form.save(commit=False)
            if guarantor_form.cleaned_data["dni"]:
                guarantor.credit = credit
                guarantor.save()
                phone_numbers = formsetPhoneGuarantor.save(commit=False)
                for phone_number in phone_numbers:
                    if phone_number.phone_number_g:
                        phone_number.guarantor = guarantor
                        phone_number.save()
            
            warranty = warranty_form.save(commit=False)
            if warranty_form.cleaned_data["article"]:
                warranty.credit = credit
                warranty.save()
        return redirect('clients:list')
    
    context = {
        'cliente_form': client_form,
        'formsetPhoneClient': formsetPhoneClient,
        'garante_form': guarantor_form,
        'formsetPhoneGuarantor': formsetPhoneGuarantor,
        'credito_form': credit_form,
        'empeno_form': warranty_form,
    }
    
    return render(request, 'credit/create_credit.html', context)

    
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


#ASOCIACION MEDIANTE CREACION DE UN CREDITO
#------------------------------------------------------------------   
class AssociateCreateView(CreateView):
    model = Credit
    form_class = CreditForm

    def form_valid(self, form):
        if form.is_valid():
            form.instance.mov = create_movement(form.instance, self.request.user.adviser)
            form.save()
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        print(self.kwargs)
        messages.success(self.request, 'Credito creado correctamente', "success")
        return  reverse_lazy('credits:list')
    

#CREACION DE UN CREDITO
#------------------------------------------------------------------     
class CreditCreateTo(CreateView):
    model = Credit
    form_class = CreditForm
    
    def form_valid(self, form):
        self.client = get_object_or_404(Client, pk=self.kwargs['pk'])
        if form.is_valid():
            print(self.kwargs)
            credit = form.save(commit=False)
            credit.client = self.client
            credit.mov = create_movement(credit, self.request.user.adviser)
            credit.save()
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Credito creado correctamente', "success")
        return  reverse_lazy('clients:list') #CORREGIR PARA QUE VUELVA A LA PESTAÑA DEL CLIENTE
    

#------------------------------------------------------------------     
class CreditUpdateView(UpdateView):
    model = Credit
    form_class = CreditForm

    def form_valid(self, form):
        if form.is_valid():
            form.instance.mov.amount = form.instance.amount
            form.instance.mov.save()
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Credito actualizado correctamente', "success")
        return  reverse_lazy('credits:list')
    
#------------------------------------------------------------------     
class CreditDeleteView(DeleteView):
    model = Credit
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Credito borrado correctamente', "danger")
        return  reverse_lazy('credits:list')
    

#------------------------------------------------------------------   
def refinance_installment (request, pk):
    credit = get_object_or_404(Credit, id = pk)
    form = RefinancingForm(credit, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            checkboxs_by_form = {key: True for key, value in request.POST.items() if key.startswith('Cuota')}

            # GET THE NUMBER OF THE LAST INSTALLMENT
            last_installment = 0
            for key in checkboxs_by_form.keys():
                if key.startswith('Cuota'):
                    last_installment = max(last_installment, int(key.split()[1]))

            refinancing = form.save(commit=False)
            refinancing.installment = get_object_or_404(Installment, credit=credit, installment_number=last_installment)
            refinancing.installment.condition = 'Refinanciada'
            refinancing.installment.is_refinancing_installment = True
            refinancing.installment.save()
            refinancing.save()
            return redirect('clients:detail', pk=credit.client.id)
        
#----------------------------------------------------------------
class RefinancingDetailView(DetailView):
    model = Installment
    template_name = 'refinance/refinance_detail.html'

    def get_context_data(self, **kwargs):
        installment = self.get_object()
        refinance = installment.refinancing

        kwargs = super().get_context_data(**kwargs)
        kwargs['form_payment_ref'] = RefinancingForm(credit=refinance)
        kwargs['refinance'] = get_object_or_404(Refinancing, pk = installment.refinancing.pk)
        return kwargs