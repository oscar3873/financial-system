from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from django.urls import reverse_lazy

#CRUD Payment
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView

from credit.models import Credit, Refinancing, Installment
from credit.utils import refresh_condition
from cashregister.utils import create_cashregister
from .utils import *
from .models import Payment
from .forms import PaymentForm

# Create your views here.
class PaymentListView(LoginRequiredMixin, ListView):
    """
    Lista de pagos.
    """
    model = Payment
    template_name = "payment/payment_list.html"
    paginate_by = 6

    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    

    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los pagos que se encuentran en la base de datos para usarlo en el contexto.
        """
        refresh_condition()
        create_cashregister()
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context["count_payments"] = self.model.objects.all().count()
        context["payments"] = self.model.objects.all()
        context["properties"] = all_properties_paymnet()
        
        return context

#BORRADO DE UNA NOTA
#------------------------------------------------------------------
class PaymentDeleteView(DeleteView):
    """
    Borrado de un pago.
    """
    model = Payment

    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_success_url(self) -> str:
        """
        Obtiene la URL de redirección después de que se ha eliminado correctamente.
        Agrega un mensaje de éxito a la cola de mensajes.
        """
        messages.success(self.request, 'Pago borrada correctamente', "danger")
        return  reverse_lazy('payments:list')

#ACTUALIZACION DE UN MOVIMIENTO
#------------------------------------------------------------------
class PaymentUpdateView(UpdateView):
    """
    Actualización de un pago.
    """	
    model = Payment
    form_class = PaymentForm
    template_name_suffix = '_update_form'

    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_form_kwargs(self):
        """
        Función que se encarga de obtener los parámetros del formulario.
        """
        kwargs = super(PaymentUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_success_url(self) -> str:
        """
        Obtiene la URL de redirección después de que se ha eliminado correctamente.
        Agrega un mensaje de éxito a la cola de mensajes.
        """
        messages.success(self.request, 'Pago actualizada satisfactoriamente', "info")
        return  reverse_lazy('payments:list')
    
#REALIZAR DE UN PAGO
#------------------------------------------------------------------
@login_required(login_url="/accounts/login/")
def make_payment_installment(request, pk):
    """
    Metodo para realizar pagos de cuotas normales y refinanciadas.
    """
    refresh_condition()
    try:
        refinancing = get_object_or_404(Refinancing, pk=pk)
        installments = refinancing.installments.exclude(condition='Pagada')
        installment_amount = refinancing.installments.first().amount
        client = refinancing.installment_ref.last().credit.client
    except:
        credit = get_object_or_404(Credit, pk=pk)
        installments = credit.installments.exclude(condition__in=['Refinanciada', 'Pagada'])
        installment_amount = credit.installments.first().amount
        client = credit.client

    form = PaymentForm(installments, request.POST or None)

    if request.method == 'POST' and form.is_valid():
        payment = form.save(commit=False)
        
        installment_ = list(installments.all())
        checkboxs_by_form = {key: value for key, value in form.cleaned_data.items() if key.startswith('Cuota')}
        pack = dict(zip(installment_, checkboxs_by_form.values()))
        count_value = list(pack.values()).count(True)
        payment._adviser = request.user.adviser

        if count_value == 0 :
            payment.amount = installment_amount
            pay_installment(payment, installments, abs(Decimal(form.cleaned_data["amount_paid"])))
        else:
            for installment in pack.keys():
                if pack[installment]:
                    payment.amount = installment.amount
                    installment.condition = 'Pagada'
                    installment.is_paid_installment = True
                    installment.payment_date = payment.payment_date
                    installment.save()
                    payment_create(payment, installment)

        score = round(200/len(installment_))*count_value
        if isinstance(installments, Installment):
            client.score += score
        else:
            client.score += round(round(200/len(installment_))/2)
        client.save()

    return redirect('clients:detail', pk=client.pk)
    
