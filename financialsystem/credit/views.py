from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

import copy

from cashregister.utils import create_movement, create_cashregister

from .utils import *

from .models import Credit, Installment, InstallmentRefinancing
from clients.models import Client
from guarantor.models import Guarantor

from .forms import *
from guarantor.forms import GuarantorForm, PhoneNumberFormSetG
from warranty.forms import WarrantyForm, WarrantyFormSet
from clients.forms import ClientForm, PhoneNumberFormSet
from payment.forms import PaymentForm

#CREAR UN CREDITO CON TODOS LOS FORMULARIOS ANIDADOS
@login_required(login_url="/accounts/login/")
def crear_credito(request):
    """
    Creacion de un cliente, credito, garante y empeño, con sus respectivos formularios.
    """
    client_form = ClientForm(request.POST or None)
    guarantor_form = GuarantorForm(request.POST or None)
    warranty_form = WarrantyForm(request.POST or None)
    credit_form = CreditForm(request.POST or None)
    formsetPhoneClient = PhoneNumberFormSet(request.POST or None, instance=Client(), prefix = "phone_number_client")
    formsetPhoneGuarantor = PhoneNumberFormSetG(request.POST or None, instance=Guarantor(), prefix = "phone_number_guarantor")
    
    if request.method == 'POST':
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
            credit.is_new = True
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
            
            messages.success(request, 'El cliente se ha guardado exitosamente.')
            return redirect('clients:list')
    else:
        print("------------Algun formulario es invalido------------")
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
    """
    Lista de creditos.
    """
    model = Credit
    template_name = 'credits/credit_list.html'
    ordering = ['-id']
    paginate_by = 5
    
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    
    
    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los creditos de la base de datos para usarlos en el contexto.
        """
        refresh_condition()
        create_cashregister()
        context = super().get_context_data(**kwargs)
        context["count_credits"] = self.model.objects.all().count()
        context["credits"] = self.model.objects.all()
        
        # Crear un objeto Paginator para dividir los resultados en páginas
        paginator = Paginator(context["credits"], self.paginate_by)
        page_number = self.request.GET.get('page')    # Obtener el número de página actual

        # Obtener la página actual del objeto Paginator
        page_obj = paginator.get_page(page_number)
        # Agregar la página actual al contexto
        context["credits"] = page_obj
        
        context["properties"] = all_properties_credit()
        return context
    
class CreditDetailView(DetailView):
    """
    Detalle	del credito.
    """
    model = Credit
    template_name = 'credits/credit_detail.html'

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get_object(self):
        return get_object_or_404(Credit, pk=self.kwargs['pk'])


#ASOCIACION MEDIANTE CREACION DE UN CREDITO
#------------------------------------------------------------------   
class AssociateCreateView(CreateView):
    """
    Asocia un credito por crear a un cliente .
    """
    model = Credit
    form_class = CreditForm

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los clientes que se encuentran en la base de datos para usarlo en el contexto.
        """
        context = super().get_context_data(**kwargs)
        context['clients'] = Client.objects.all()
        context['warranty_form'] = WarrantyForm
        return context

    def form_valid(self, form):
        """
        Validacion del formulario de credito.
        """
        if form.is_valid():
            # Recuperar el ID del cliente seleccionado
            
            selected_client_id = self.request.POST.get('selected_client_id')
            # Asignar el crédito al cliente correspondiente
            client = get_object_or_404(Client, pk=selected_client_id)
            credit = form.save(commit=False)
            credit.is_new = True
            credit.client = client
            credit.mov = create_movement(credit, self.request.user.adviser)
            credit.save()

            # Validar el formulario de garantía
            warranty_form = WarrantyForm(self.request.POST)
            warranty = warranty_form.save(commit=False)
            if warranty_form.cleaned_data['article']:
                # Asignar la garantía al crédito correspondiente
                warranty.credit = credit
                warranty.save()
            
        return super().form_valid(form)

    
    def get_success_url(self) -> str:
        """ 
        Redirecciona al listado de credito, con un mensaje de creacion exitosa.
        """
        messages.success(self.request, 'Credito creado correctamente', "success")
        return  reverse_lazy('credits:list')


@login_required(login_url="/accounts/login/")
def buscar_clientes_view(request):
    search_term = request.GET.get('search_term')

    if search_term:
        # Realizar la búsqueda de clientes que coincidan con el término de búsqueda
        clientes = Client.objects.filter(
            first_name__startswith=search_term
        ) | Client.objects.filter(
            last_name__startswith=search_term
        ) | Client.objects.filter(
            dni__startswith =search_term
        )
        
        # Serializar los resultados como un diccionario de Python
        data = {
            'clientes': [
                {
                    'id': cliente.id,
                    'full_name': f'{cliente.first_name} {cliente.last_name}',
                    'dni': cliente.dni,
                } for cliente in clientes
            ]
        }
    else:
        data = {'clientes': []}

    return JsonResponse(data)



#CREACION DE UN CREDITO
#------------------------------------------------------------------     
class CreditCreateTo(CreateView):
    """
    Creacion de un credito para un cliente desde detail.
    """	
    model = Credit
    form_class = CreditForm
    template_name = 'credit/credit_form.html'

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_add'] = True
        context['warranty_form'] = WarrantyForm
        return context
    
    def form_valid(self, form):
        """
        Validacion de formulario de credito.
        """
        self.client = get_object_or_404(Client, pk=self.kwargs['pk'])

        if form.is_valid():
            credit = form.save(commit=False)
            credit.is_new = True
            credit.client = self.client
            credit.mov = create_movement(credit, self.request.user.adviser)
            credit.save()
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        """
        Redirecciona al listado de credito, con un mensaje de creacion exitosa.
        """
        messages.success(self.request, 'Credito creado correctamente', "success")
        return  reverse_lazy('clients:detail', kwargs=self.kwargs)
    

#------------------------------------------------------------------   NUEVOOO
@login_required(login_url="/accounts/login/")
def edit_credit(request, pk):
    
    credit_original = Credit.objects.get(id=pk)
    credit_copy = copy.copy(credit_original)
    InstallmentFormSet = formset_factory(InstallmentUpdateForm, extra=0)
    if request.method == 'POST':
        form = CreditWithInstallmentsForm(request.POST, instance=credit_original)
        formset = InstallmentFormSet(request.POST, prefix='installments')
        if form.is_valid() and formset.is_valid():
            credit = form.save(commit=False)

            if (credit_copy.is_paid != credit.is_paid) or (credit_copy.amount != credit.amount) or (credit_copy.credit_interest != credit.credit_interest) or (credit_copy.installment_num != credit.installment_num):
                credit.is_new = True        
                credit.save()

            for form in formset:
                installment = form.save(commit=False)   
                installment.credit = credit
                
            messages.success(request,'Cambios realizados exitosamente')
            return redirect('credits:edit_credit', pk=credit.pk)
    else:
        form = CreditWithInstallmentsForm(instance=credit_original)
        formset = InstallmentFormSet(prefix='installments', initial=credit_original.installments.values())
    context = {
        'form': form,
        'formset': formset,
        'client': credit_original.client
        }
    return render(request, 'credit/edit_credit.html', context)


#------------------------------------------------------------------
@login_required(login_url="/accounts/login/")     
def client_delete(request, pk):
    try:
        cred = get_object_or_404(Credit, pk=pk)
        cred.delete()
        messages.success(request, 'Credito borrado correctamente', "success")
        return  redirect('credits:list')
    except:
        messages.error(request, 'Hubo un error al intentar', "danger")
        return  redirect('credits:list')
    

#------------------------------------------------------------------   
@login_required(login_url="/accounts/login/")
def refinance_installment (request, pk):
    """
    Refiancia cuotas y actualiza sus estados.
    """
    refresh_condition()
    credit = get_object_or_404(Credit, id = pk)
    form = RefinancingForm(credit, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            installments = Installment.objects.filter(credit=credit, condition__in=['Vencida','A Tiempo'])
            checkboxs_by_form = {key: value for key, value in form.cleaned_data.items() if key.startswith('Cuota')}
            pack = dict(zip(installments, checkboxs_by_form.values()))
            
            refinancing = form.save(commit=False)
            refinancing.save()
            for installment in pack.keys():
                if pack[installment]:
                    installment.condition = 'Refinanciada'
                    installment.is_refinancing_installment = True
                    installment.refinance = refinancing
                    installment.save()
                
    return redirect('clients:detail', pk=credit.client.pk)
        
#----------------------------------------------------------------
class RefinancingDetailView(DetailView):
    """
    Detalle de refinanciacion.
    """
    model = Installment
    template_name = 'refinance/refinance_detail.html'

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los refinanciamientos de la base de datos para usarlos en el contexto y poder pagarlos con PaymentsForm.
        """
        refresh_condition()
        refinance = self.get_object().refinance
        refinance_installments_available = refinance.installments.exclude(condition__in=['Pagada'])
        context = super().get_context_data(**kwargs)
        print(refinance_installments_available.all())
        context['form_payment'] = PaymentForm(installments=refinance_installments_available.all())
        context['refinance'] = refinance
        context["amount_installment"] = refinance.installments.last().amount
        return context

#----------------------------------------------------------------
class InstallmentRefUpdateView(UpdateView):
    model = InstallmentRefinancing
    form_class = InstallmentRefinancingForm
    template_name = 'installment/installment_ref_update.html'
    success_url = reverse_lazy('clients:list')

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['installment_ref'] = self.object
        print(self.object.id)
        return context
    
    def get_success_url(self):
        return reverse('credits:refinance_detail', args=[self.object.refinancing.installment_ref.last().pk])
    
#----------------------------------------------------------------
class InstallmentUpdateView(UpdateView):
    model = Installment
    form_class = InstallmentUpdateForm
    template_name = 'installment/installment_update.html'

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['installment'] = self.object
        return context
    
    def get_success_url(self):
        return reverse('clients:detail', args=[self.object.credit.client.pk])