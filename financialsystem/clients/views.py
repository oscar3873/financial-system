from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from babel.dates import format_date
from clients.filters import ListingFilter
from credit.utils import refresh_condition

from .utils import all_properties_client
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.urls import reverse_lazy


#CRUD CLIENT
from django.views.generic import ListView, DetailView, DeleteView, UpdateView

#FORMS
from .forms import ClientForm, PhoneNumberFormSetUpdate
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
    paginate_by = 4
    filter_class = ListingFilter
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los clientes que se encuentran en la base de datos para usarlo en el contexto.
        """
        refresh_condition()
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        clients = self.model.objects.all()
        # Etiqueta para el día actual
        today = timezone.now().date()

        # Etiqueta para el mes actual
        month = datetime.today().month
        label_month = format_date(timezone.now(), format='MMMM Y', locale='es').capitalize()
        label_day = f'Hoy {timezone.now().date().day} de {label_month}'
        year = timezone.now().year
        label_year = str(year)
        label_historial = "Historico"
        score_counts_list = [
            {'label': 'Riesgoso', 'value': clients.filter(score_label='Riesgoso').count()},
            {'label': 'Regular', 'value': clients.filter(score_label='Regular').count()},
            {'label': 'Bueno', 'value': clients.filter(score_label='Bueno').count()},
            {'label': 'Muy Bueno', 'value': clients.filter(score_label='Muy Bueno').count()},
            {'label': 'Excelente', 'value': clients.filter(score_label='Exelente').count()},
        ]
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
        context["clients"] = clients
        context["score_counts_list"] = score_counts_list
        context["properties"] = all_properties_client()
        context["listing_filter"] = ListingFilter(self.request.GET, context['clients'])
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
    

#ACTUALIZACION DE UN CLIENTE
#-----------------------------------------------------------------
class ClientUpdateView(UpdateView):
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
            context['phone_formset'] = PhoneNumberFormSetUpdate(instance=self.object)
        return context

    def form_invalid(self, form):
        """
        Muestra un error en caso de formulario invalido.
        """
        print("Esto re invalido amigoooo", form.errors)
        return super().form_invalid(form)
    
    def form_valid(self, form):
        """
        Actualiza el cliente y sus telefonos.
        """
        print("Estoy aca amigo")
        response = super().form_valid(form)
        phone_formset = PhoneNumberFormSetUpdate(self.request.POST, instance=self.object)
        phone_formset.save()
        
        return response

    def get_success_url(self) -> str:
        """
        Obtiene la URL de redirección después de que se ha actualizado correctamente.
        Agrega un mensaje de éxito a la cola de mensajes.
        """	
        messages.success(self.request, '{}, realizada el {}, actualizada satisfactoriamente'.format(self.object, self.object.created_at.date()), "info")
        return reverse_lazy('clients:list')


#DETALLE DE CLIENTE
#------------------------------------------------------------------
class ClientDetailView(DetailView):
    """
    Detalle de un cliente.
    """
    model = Client
    template_name = 'clients/client_detail.html'
    
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


        forms_payments = []
        form_refinancings = []
        installments_by_credit = {}
        for credit in credits_active:
            installments_list = []
            installments = credit.installments.exclude(condition__in=['Refinanciada', 'Pagada'])
            # refinancings = Refinancing.objects.filter(installment_ref__credit=credit)

            forms_payments.append(PaymentForm(installments=installments) if installments else None)
            form_refinancings.append(RefinancingForm(credit=credit) if installments else None)

            for installment in credit.installments.all():
                refinance = installment.refinance
                if refinance:
                    refinance_installments_available = refinance.installments.exclude(condition__in=['Pagada'])
                    payment_form = PaymentForm(installments=refinance_installments_available.all())
                else:
                    payment_form = None
                installments_list.append((installment, [refinance, payment_form]))
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

    def get_object(self):
        """
        Función que se encarga de obtener el cliente.
        """	
        return get_object_or_404(Client, id=self.kwargs['pk'])
    

#BORRADO DE UN CLIENTE
#------------------------------------------------------------------
class ClientDelete(DeleteView):
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
        messages.success(self.request, 'Cliente eliminado correctamente', "danger")
        return  reverse_lazy('clients:list')

    
#BORRADO DE NUMEROS DE UN CLIENTE
#------------------------------------------------------------------
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
class QueryView(ListView):
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
            messages.error(request, "Cliente no encontrado")
        return (redirect('home' if self.request.user.is_authenticated else 'query'))