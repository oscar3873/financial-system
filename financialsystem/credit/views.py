from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction


import copy

from cashregister.utils import create_movement, create_cashregister
from clients.filters import ListingFilter

from .utils import *

from .models import Credit, Installment, InstallmentRefinancing
from clients.models import Client
from guarantor.models import Guarantor

from .forms import *
from guarantor.forms import GuarantorForm, PhoneNumberFormSetG
from warranty.forms import WarrantyForm
from clients.forms import ClientForm, PhoneNumberFormSet

#CREAR UN CREDITO CON TODOS LOS FORMULARIOS ANIDADOS
@login_required(login_url="/accounts/login/")
def crear_credito(request):
    """
    Creacion de un cliente, credito, garante y empeño, con sus respectivos formularios.
    """
    client_form = ClientForm(request.POST or None)
    guarantor_form = GuarantorForm(request.POST or None, prefix = 'credit_created')
    warranty_form = WarrantyForm(request.POST or None)
    credit_form = CreditForm(request.POST or None, initial = {'adviser':request.user.adviser})
    formsetPhoneClient = PhoneNumberFormSet(request.POST or None, instance=Client(), prefix = "phone_number_client")
    formsetPhoneGuarantor = PhoneNumberFormSetG(request.POST or None, instance=Guarantor(), prefix = "phone_number_guarantor")

    if request.method == 'POST':
        if client_form.is_valid() and credit_form.is_valid() and warranty_form.is_valid()  and formsetPhoneClient.is_valid() and guarantor_form.is_valid() and formsetPhoneGuarantor.is_valid():
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
            ask_is_old(credit, credit_form.cleaned_data['adviser'])

            
            guarantor = guarantor_form.save(commit=False)
            if guarantor_form.cleaned_data["dni"]:
                credit.guarantor = credit
                credit.save()
                phone_numbers = formsetPhoneGuarantor.save(commit=False)
                for phone_number in phone_numbers:
                    if phone_number.phone_number_g:
                        phone_number.guarantor = guarantor
                        phone_number.save()

            warranty = warranty_form.save(commit=False)
            if warranty_form.cleaned_data["article"]:
                warranty.credit = credit
                warranty.save()

            messages.success(request, 'El cliente se ha guardado exitosamente.',"success")
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
    template_name = 'credit/credit_list.html'
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
        credits = self.model.objects.all()
        
        # Crear un objeto Paginator para dividir los resultados en páginas
        paginator = Paginator(credits, self.paginate_by)
        page_number = self.request.GET.get('page')    # Obtener el número de página actual

        # Obtener la página actual del objeto Paginator
        page_obj = paginator.get_page(page_number)
        # Agregar la página actual al contexto
        context["credits"] = page_obj

        context["properties"] = all_properties_credit()
        return context

class CreditDetailView(DetailView, LoginRequiredMixin):
    """
    Detalle	del credito.
    """
    model = Credit
    template_name = 'credit/credit_detail.html'

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        installments = context["credit"].installments.all()
        context["installments"] = installments
        ref_in_installments = Installment.objects.filter(credit=context["credit"], is_refinancing_installment=True)
        # Crea una lista de todas las cuotas refinanciadas de los objetos en la lista ref_in_installments
        installments_ref = [inst_ref for inst in ref_in_installments for inst_ref in inst.refinance.installments.all()]
        context["installments_ref"] = installments_ref
        return context

    def get_object(self):
        return get_object_or_404(Credit, pk=self.kwargs['pk'])


#ASOCIACION MEDIANTE CREACION DE UN CREDITO
#------------------------------------------------------------------
from django.db import transaction
from django.shortcuts import get_object_or_404

class AssociateCreateView(CreateView, LoginRequiredMixin):
    """
    Asocia un crédito por crear a un cliente.
    """
    model = Credit
    form_class = CreditForm

    # CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get_initial(self) :
        iniitial = super().get_initial()
        iniitial['adviser'] = self.request.user.adviser
        return iniitial


    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los clientes que se encuentran en la base de datos para usarlo en el contexto.
        """
        context = super().get_context_data(**kwargs)
        context['form'] = CreditForm(initial= self.get_initial())
        context['clients'] = Client.objects.all()
        context['warranty_form'] = WarrantyForm(self.request.POST or None)
        context['garante_form'] = GuarantorForm(self.request.POST or None, prefix="credit_created")
        context['formsetPhoneGuarantor'] = PhoneNumberFormSetG(instance=Guarantor(), prefix="phone_number_guarantor")

        return context

    @transaction.atomic
    def form_valid(self, form):
        """
        Validación del formulario de crédito.
        """
        if form.is_valid():
            # Recuperar el ID del cliente seleccionado
            selected_client_id = self.request.POST.get('selected_client_id')
            # Asignar el crédito al cliente correspondiente
            client = get_object_or_404(Client, pk=selected_client_id)
            credit = form.save(commit=False)
            credit.client = client
            ask_is_old(credit, form.cleaned_data['adviser'])

            # Validar el formulario de garantía
            warranty_form = WarrantyForm(self.request.POST)
            warranty = warranty_form.save(commit=False)
            if warranty_form.cleaned_data['article']:
                # Asignar la garantía al crédito correspondiente
                warranty.credit = credit
                warranty.save()

            # Validar el formulario de garante
            garante_form = GuarantorForm(self.request.POST, prefix="credit_created")
            guarantor = garante_form.save(commit=False)
            if garante_form.cleaned_data["dni"]:
                if garante_form.is_valid():
                    credit.guarantor = guarantor
                    credit.save()
                phone_numbers_form = PhoneNumberFormSetG(self.request.POST, instance=guarantor, prefix="phone_number_guarantor")
                phone_numbers = phone_numbers_form.save(commit=False)
                for phone_number in phone_numbers:
                    if phone_number.phone_number_g:
                        phone_number.guarantor = guarantor
                        phone_number.save()

            return super().form_valid(form)
        else:
            return self.form_invalid(form)



    def get_success_url(self) -> str:
        """
        Redirecciona al listado de credito, con un mensaje de creacion exitosa.
        """
        messages.success(self.request, 'Credito creado correctamente',"success")
        return  reverse_lazy('credits:list')


#CREACION DE UN CREDITO
#------------------------------------------------------------------
class CreditCreateTo(LoginRequiredMixin, CreateView):
    """
    Creacion de un credito para un cliente desde detail.
    """
    model = Credit
    form_class = CreditForm
    template_name = 'credit/credit_form.html'

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get_initial(self) :
        iniitial = super().get_initial()
        iniitial['adviser'] = Client.objects.get(pk=self.kwargs['pk']).adviser
        return iniitial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cliente_form'] = CreditForm(initial= self.get_initial())
        context['is_add'] = True
        context['warranty_form'] = WarrantyForm
        context['garante_form'] = GuarantorForm(prefix = 'credit_created')
        context['formsetPhoneGuarantor'] = PhoneNumberFormSetG(instance=Guarantor(), prefix = "phone_number_guarantor")

        return context

    @transaction.atomic
    def form_valid(self, form):
        """
        Validación del formulario de crédito.
        """
        if form.is_valid():
            # Recuperar el ID del cliente seleccionado
            client = get_object_or_404(Client, pk=self.kwargs['pk'])
            credit = form.save(commit=False)
            credit.client = client
            ask_is_old(credit, form.cleaned_data['adviser'])

            # Validar el formulario de garantía
            warranty_form = WarrantyForm(self.request.POST)
            warranty = warranty_form.save(commit=False)
            if warranty_form.cleaned_data['article']:
                warranty.credit = credit
                warranty.save()

            # Validar el formulario de garante
            selected_client_id = self.request.POST.get('selected_guarantor_id')
            if selected_client_id != None:
                guarantor = Guarantor.objects.get(pk=selected_client_id)
                credit.guarantor = guarantor
                credit.save()
            else:
                garante_form = GuarantorForm(self.request.POST, prefix="credit_created")
                guarantor = garante_form.save(commit=False)
                if garante_form.cleaned_data["dni"]:
                    if garante_form.is_valid():
                        credit.guarantor = guarantor
                        credit.save()
                        phone_numbers_form = PhoneNumberFormSetG(self.request.POST, instance=guarantor, prefix="phone_number_guarantor")
                        phone_numbers = phone_numbers_form.save(commit=False)
                        for phone_number in phone_numbers:
                            if phone_number.phone_number_g:
                                phone_number.guarantor = guarantor
                                phone_number.save()

            return super().form_valid(form)
        else:
            return self.form_invalid(form)

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
    form = CreditUpdateForm(instance=credit_original)

    if request.method == 'POST':
        form = CreditUpdateForm(request.POST, instance=credit_original)
        if form.is_valid():
            credit = form.save(commit=False)

            if (credit_copy.start_date != credit.start_date) or (credit_copy.amount != credit.amount) or (credit_copy.interest != credit.interest) or (credit_copy.installment_num != credit.installment_num):
                credit.is_old_credit = False
                credit.save()

            messages.info(request,'Cambios realizados exitosamente',"info")
            return redirect('credits:list')

    context = {
        'form': form,
        'client': credit_original.client
        }
    return render(request, 'credit/edit_credit.html', context)


#------------------------------------------------------------------
@login_required(login_url="/accounts/login/")
def credit_delete(request, pk):
    try:
        cred = get_object_or_404(Credit, pk=pk)
        client = cred.client
        cred.delete()
        messages.warning(request, 'Credito borrado correctamente', "warning")
        return  redirect('clients:detail', pk=client.pk)
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
            checkboxs_by_form = {key: value for key, value in form.cleaned_data.items() if key.startswith('cuota')}
            pack = dict(zip(installments, checkboxs_by_form.values()))
            refinancing = form.save(commit=False)
            refinancing.credit = credit
            refinancing.is_new = True
            refinancing.save()
            for installment in pack.keys():
                if pack[installment]:
                    installment.condition = 'Refinanciada'
                    installment.is_refinancing_installment = True
                    installment.refinance = refinancing
                    installment.save()

    return redirect('clients:detail', pk=credit.client.pk)

#----------------------------------------------------------------
class RefinancingUpdateView(LoginRequiredMixin, UpdateView):
    """
    Detalle de refinanciacion.
    """
    model = Refinancing
    template_name = 'refinance/refinance_update.html'
    form_class = RefinancingFormUpdate

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self.object.installment_ref.first().credit.client
        return context

    def form_valid(self, form):
        if form.is_valid():
            refinance_copy = copy.copy(self.object)
            refinance = form.save(commit=False)

            if (refinance_copy.end_date != refinance.end_date) or (refinance_copy.start_date != refinance.start_date) or (refinance_copy.amount != refinance.amount) or (refinance_copy.interest != refinance.interest) or (refinance_copy.installment_num != refinance.installment_num):
                refinance.is_new = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('clients:detail', args=[self.kwargs['client'].pk])


#-------------------------------------------------------------------
def refinancing_delete(request, pk):
    refinancing = Refinancing.objects.get(pk=pk)
    client = refinancing.installment_ref.first().credit.client
    refinancing.delete()
    return redirect('clients:detail', pk = client.pk)


#----------------------------------------------------------------
class InstallmentRefUpdateView(LoginRequiredMixin, UpdateView):
    model = InstallmentRefinancing
    form_class = InstallmentRefinancingUpdateForm
    template_name = 'installment/installment_ref_update.html'

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        installment = get_object_or_404(Installment, pk = self.kwargs['pk'])
        if form.is_valid():
            if installment.end_date.date() != form.cleaned_data['end_date'].date():
                form.instance.daily_interests = 0
                form.instance.lastup = form.instance.end_date.date()

            if installment.payment_date is not None:
                if installment.payment_date.date() != form.cleaned_data['payment_date'].date():
                    form.instance.condition = 'Pagada'

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['installment'] = self.object
        return context

    def get_success_url(self):
        return reverse('clients:detail', args=[self.object.refinancing.installment_ref.last().credit.client.pk])

#----------------------------------------------------------------
class InstallmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Installment
    form_class = InstallmentUpdateForm
    template_name = 'installment/installment_update.html'

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'


    def form_valid(self, form):
        installment = get_object_or_404(Installment, pk=self.kwargs['pk'])
        if form.is_valid():
            if not installment.payment_date and form.cleaned_data['payment_date']:
                form.instance.condition = 'Pagada'

            elif installment.payment_date and not form.cleaned_data['payment_date']:
                form.instance.condition = 'A Tiempo'

            elif form.cleaned_data['condition'] == 'A Tiempo':
                form.instance.payment_date = None

            if installment.end_date.date() != form.cleaned_data['end_date'].date():
                form.instance.daily_interests = 0
                form.instance.lastup = form.instance.end_date.date()
            
            if installment.end_date < installment.start_date:
                form.instance.end_date = installment.end_date
                form.instance.start_date = installment.start_date
                messages.error(self.request,"Error al guardar fechas","danger")

        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['installment'] = self.object
        return context

    def get_success_url(self):
        return reverse('clients:detail', args=[self.object.credit.client.pk])