import itertools
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.db.models import Count

from django.core.paginator import Paginator

from babel.dates import format_date
from .filters import ListingFilter
from credit.utils import refresh_condition
from cashregister.utils import create_cashregister
from credit.models import Installment
from credit.models import InstallmentRefinancing
from payment.models import Payment
from .utils import all_properties_client

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy


#CRUD CLIENT
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView

#FORMS
from .forms import *
#MODEL
from .models import Client, PhoneNumberClient
from credit.models import Refinancing
from credit.forms import RefinancingForm

from payment.forms import PaymentForm



# Create your views here.

#LISTA DE CLIENTES
#------------------------------------------------------------------
class ClientListView(LoginRequiredMixin, ListView):
    """
    Lista de clientes con autenticacion de logeo.
    """
    model = Client
    template_name = 'clients/client_list.html'
    ordering = ['-created_at']
    paginate_by = 8
    filter_class = ListingFilter
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
        
    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los clientes que se encuentran en la base de datos para usarlo en el contexto.
        """
        refresh_condition()
        create_cashregister()

        # Obtén los objetos clients filtrados
        clients = self.model.objects.all()
        filtered_clients = ListingFilter(self.request.GET, clients)

        # Pagina los objetos clients filtrados
        paginator = Paginator(filtered_clients.qs, self.paginate_by)
        page = self.request.GET.get('page')
        clients_paginated = paginator.get_page(page)

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
        
        #Cantidad de datos por score
        score_counts_list = [
            {'label': 'Riesgoso', 'value': clients.filter(score_label='Riesgoso').count()},
            {'label': 'Regular', 'value': clients.filter(score_label='Regular').count()},
            {'label': 'Bueno', 'value': clients.filter(score_label='Bueno').count()},
            {'label': 'Muy Bueno', 'value': clients.filter(score_label='Muy Bueno').count()},
            {'label': 'Excelente', 'value': clients.filter(score_label='Exelente').count()},
        ]
        
        #Top clientes
        clients_top = Client.objects.filter(score__gt=1200)[:3]
        clients_top_credits = Client.objects.annotate(num_credits=Count('credits')).order_by('-num_credits')[:3]
        # Contextos
        context["count_clients_dict"] = count_clients_dict
        context["clients_top"] = clients_top
        context["clients_top_credits"] = clients_top_credits
        context["score_counts_list"] = score_counts_list
        context["properties"] = all_properties_client()
        # Reemplaza context["clients"] con los objetos clients paginados
        context["clients"] = clients_paginated
        context["listing_filter"] = filtered_clients
        return context
    
    def get_queryset(self):
        """
        Función que se encarga de obtener los parámetros del formulario.
        """
        queryset = super().get_queryset()
        self.filterset = self.filter_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.order_by(*self.ordering)
    
    def get_success_url(self) -> str:
        """
        Función que se encarga de devolver la URL de la vista actual.
        """
        return reverse_lazy('clients:list')
    


def clientCreate(request):
    client_form = ClientForm(request.POST or None)
    formset_phone_client = PhoneNumberFormSet(request.POST or None, instance=Client(), prefix="phone_number_client")

    if request.method == 'POST':
        if client_form.is_valid() and formset_phone_client.is_valid():
            client = client_form.save(commit=False)
            client.adviser = request.user.adviser
            client.save()
            
            phone_numbers = formset_phone_client.save(commit=False)
            for phone_number in phone_numbers:
                if phone_number.phone_number_c:
                    phone_number.client = client
                    phone_number.save()

            messages.success(request, 'El cliente se ha guardado exitosamente.',"success")
            return redirect('clients:list')
        else:
            messages.error(request, 'Ocurrió un error al guardar el cliente.',"danger")

    context = {
        'form': client_form,
        'formsetPhoneClient': formset_phone_client,
    }

    return render(request, 'clients/client_form.html', context)



#ACTUALIZACION DE UN CLIENTE
#-----------------------------------------------------------------
class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """
    Actualiza el client y sus telefonos.
    """
    model = Client
    form_class = ClientForm
    template_name_suffix = '_update'

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los clientes (telefonos) que se encuentran en la base de datos para usarlo en el contexto.
        """
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['phone_formset'] = PhoneNumberFormSetUpdate(self.request.POST, instance=self.object)
        else:
            context['form'] = ClientForm(instance = self.object)
            context['phone_formset'] = PhoneNumberFormSetUpdate(instance=self.object)
        context['client'] = self.object
        return context

    def form_invalid(self, form):
        """
        Muestra un error en caso de formulario invalido.
        """
        return super().form_invalid(form)
    
    def form_valid(self, form):
        """
        Actualiza el cliente y sus telefonos.
        """
        response = super().form_valid(form)
        phone_formset = PhoneNumberFormSetUpdate(self.request.POST, instance=self.object)
        phone_formset.save()
        
        return response

    def get_success_url(self) -> str:
        """
        Obtiene la URL de redirección después de que se ha actualizado correctamente.
        Agrega un mensaje de éxito a la cola de mensajes.
        """	
        messages.success(self.request, '{}, realizada el {}, actualizada satisfactoriamente'.format(self.object, self.object.created_at.date()),"success")
        return reverse_lazy('clients:list')


#DETALLE DE CLIENTE
#------------------------------------------------------------------
class ClientDetailView (LoginRequiredMixin, DetailView):
    """
    Detalle de un cliente.
    """
    model = Client
    template_name = 'clients/client_detail.html'
    paginate_by = 4
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    
    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los clientes que se encuentran en la base de datos para usarlo en el contexto.
        Con Formularios de Pago y Refianciacion para realizar las respectivas actividades dentro del msimo template.
        """

        refresh_condition()
        context = super().get_context_data(**kwargs)
        context["credits"] = context["client"].credits.all()
        credits_active = context["credits"].filter(is_active=True).order_by("created_at")
        context["credits_active"] = credits_active
        context["count_credits"] = context["credits"].count()
        context["count_credits_active"] = context["credits_active"].count()
        paginator = Paginator(context["credits"], self.paginate_by)
        page_number = self.request.GET.get('page')    # Obtener el número de página actual

        # Obtener la página actual del objeto Paginator
        page_obj = paginator.get_page(page_number)
        # Agregar la página actual al contexto
        context["credits"] = page_obj

        if credits_active:
            next_installments = []
            for credit in credits_active:
                normal_installments = credit.installments.exclude(condition__in=['Refinanciada', 'Pagada'])
                refinance_installments = Installment.objects.filter(refinance__installment_ref__credit=credit).exclude(condition='Pagada')

                all_installments = normal_installments | refinance_installments
                next_installments.extend(all_installments.filter(end_date__gte=datetime.now()).values('credit', 'end_date', 'amount', 'installment_number'))

            next_installments.sort(key=lambda x: x['end_date'])
            next_three_installments = next_installments[:3]

            context['next_three_installments'] = next_three_installments

            last_three_payments_by_credit_list = []
            for credit in credits_active:
                # Get the related payments for the credit, order by payment_date in descending order, and get the first three
                last_three_normal_payments = Payment.objects.filter(installment__in=credit.installments.all()).order_by('-payment_date')[:3]
                
                refinancing_installments = Installment.objects.filter(credit=credit, refinance__isnull=False)
                refinancing_installments_qs = list(itertools.chain(*[installment.refinance.installments.all() for installment in refinancing_installments]))
                refinancing_installments_qs = InstallmentRefinancing.objects.filter(id__in=[installment_ref.id for installment_ref in refinancing_installments_qs])

                last_three_refinancing_payments = Payment.objects.filter(installment_ref__in=refinancing_installments_qs.all()).order_by('-payment_date')[:3]
                # Combine the lists of payments and sort them by payment_date in descending order
                combined_payments = sorted(list(itertools.chain(last_three_refinancing_payments, last_three_normal_payments)), key=lambda x: x.payment_date, reverse=True)


                # Get the first three payments from the combined list
                last_three_payments = combined_payments[:3]

                # Append the last three payments to the list for this credit
                last_three_payments_by_credit_list.append(last_three_payments)

            # Add the last_three_payments_by_credit_list to the context
            context["last_three_payments_by_credit_list"] = last_three_payments_by_credit_list
        
        forms_payments = []
        form_refinancings = []
        installments_by_credit = {}
        for credit in credits_active:
            installments_list = []
            installments = credit.installments.exclude(condition__in=['Refinanciada', 'Pagada'])
            # refinancings = Refinancing.objects.filter(installment_ref__credit=credit)

            forms_payments.append(PaymentForm(installments=installments) if installments else None)
            form_refinancings.append(RefinancingForm(credit=credit) if installments else None)

            prev_refinance = None
            for installment in credit.installments.all():
                refinance = installment.refinance

                if refinance:
                    refinance_installments_available = refinance.installments.exclude(condition__in=['Pagada'])
                    payment_form = PaymentForm(installments=refinance_installments_available.all())
                else:
                    payment_form = None

                if refinance == prev_refinance:
                    installments_list.append((installment, [None, None]))
                else:
                    installments_list.append((installment, [refinance, payment_form]))
                prev_refinance = refinance

            installments_by_credit.setdefault(credit, []).extend(installments_list)

            
        context["installments_available"] = True

        dicc = dict(zip(credits_active, forms_payments))

        for i, key in enumerate(dicc):
            dicc[key] = [dicc[key]]
            dicc[key].append(form_refinancings[i])

        for key, value in dicc.items():
            if key in installments_by_credit:
                value.append(installments_by_credit[key])
            dicc[key] = value
        
        context["client_payment"] = dicc
        return context


def go_legals(request, pk):
    if request.method == 'POST':
        print(request.POST.get('go_legals'))
        client = Client.objects.get(pk=pk)
        client.is_legals = True if request.POST.get('go_legals') == 'true' else False
        client.save()
    return redirect('clients:detail', pk=pk)  

#BORRADO DE UN CLIENTE
#------------------------------------------------------------------
class ClientDelete(LoginRequiredMixin, DeleteView):
    """
    Borra un cliente.
    """
    model = Client
    
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_success_url(self) -> str:
        """
        Obtiene la URL de redirección después de que se ha borrado correctamente.
        Agrega un mensaje de éxito a la cola de mensajes.
        """	
        messages.warning(self.request, 'Cliente eliminado correctamente',"warning")
        return  reverse_lazy('clients:list')

    
#BORRADO DE NUMEROS DE UN CLIENTE
#------------------------------------------------------------------
@login_required(login_url="/accounts/login/")
def delete_phone_number(request, pk):
    """
    Borra un número de telefono de un cliente.
    """	
    try:
        phone_number = PhoneNumberClient.objects.get(id=pk)
    except PhoneNumberClient.DoesNotExist:
        return redirect('clients:update', pk=phone_number.client.id)
    phone_number.delete()
    return redirect('clients:update', pk=phone_number.client.id)

#CONSULTA
#------------------------------------------------------------------
class QueryView(ListView , LoginRequiredMixin):
    """
    Consulta de clientes.
    """
    model = Client
    template_name = 'core/home.html'

    # Se especifica la URL de inicio de sesión y el campo de redirección
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
        
    def get(self, request, *args, **kwargs):
        """
        Obtiene el numero DNI ingresado en el search e intenta matchear.
        """
        dni = self.request.GET.get("search")
        try: 
            search = self.model.objects.get(dni=dni)
            return redirect('clients:detail', pk=search.pk) # redirecciona al detalle del cliente en caso de encontrarlo
        except :
            messages.error(request, "Cliente no encontrado", "danger")
        return (redirect('home' if self.request.user.is_authenticated else 'query'))