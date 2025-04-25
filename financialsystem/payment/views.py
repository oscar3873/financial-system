import locale
from datetime import datetime as dt
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import F

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from django.urls import reverse_lazy

#CRUD Payment
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView

from credit.models import Credit, InstallmentRefinancing, Refinancing, Installment
from cashregister.utils import create_cashregister
from commissions.models import Interest
from .utils import *
from .models import Payment
from .forms import PaymentForm
from core.utils import round_to_nearest_hundred

# Configurar el locale en español
locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
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
        create_cashregister()
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context["count_payments"] = self.model.objects.all().count()
        context["payments"] = self.model.objects.all()
        context["properties"] = all_properties_paymnet()

        return context

#BORRADO DE UNA NOTA
#------------------------------------------------------------------
class PaymentDeleteView(LoginRequiredMixin, DeleteView):
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
        messages.warning(self.request, 'Pago borrada correctamente', "warning")
        return  reverse_lazy('payments:list')

#ACTUALIZACION DE UN MOVIMIENTO
#------------------------------------------------------------------
class PaymentUpdateView(LoginRequiredMixin, UpdateView):
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
        messages.info(self.request, 'Pago actualizada satisfactoriamente',"info")
        return  reverse_lazy('payments:list')

#REALIZAR DE UN PAGO
#------------------------------------------------------------------
@login_required(login_url="/accounts/login/")
def make_payment_installment(request, pk):
    """
    Método para realizar pagos de cuotas normales y refinanciadas, incluyendo pagos parciales.
    La condición de la cuota solo se cambia a 'Pagada' cuando el total de los pagos llega o excede
    el monto de la cuota.
    """
    try:
        refinancing = get_object_or_404(Refinancing, pk=pk)
        installments_score = refinancing.installments.all().count()
        installments = refinancing.installments.exclude(condition='Pagada')
        # Se toma el monto de la primera cuota como referencia
        installment_amount = round_to_nearest_hundred(installments.first().amount)
        installment_number = installments.first().installment_number
        client = refinancing.installment_ref.last().credit.client
    except:
        credit = get_object_or_404(Credit, pk=pk)
        installments_score = credit.installments.all().count()
        installments = credit.installments.exclude(condition__in=['Refinanciada', 'Pagada'])
        installment_amount = round_to_nearest_hundred(installments.first().amount)
        installment_number = installments.first().installment_number
        client = credit.client

    form = PaymentForm(installments, request.POST or None)

    if request.method == 'POST' and form.is_valid():
        payment = form.save(commit=False)
        payment_date = form.cleaned_data['payment_date']
        payment_time = form.cleaned_data['payment_time']
        # Combina payment_date y payment_time en un solo objeto datetime
        payment.payment_date = dt.combine(payment_date, payment_time)
        checked_discount = request.POST.get('promo_discount')

        # Obtiene el monto ingresado para pago parcial, si existe; se considera 0 si no se ingresa nada.
        amount_paid = abs(Decimal(form.cleaned_data.get("amount_paid") or 0))
        # Obtiene los valores de los checkboxes de cuotas
        installment_list = list(installments.all())
        checkboxs_by_form = {key: value for key, value in form.cleaned_data.items() if key.startswith('cuota')}
        pack = dict(zip(installment_list, checkboxs_by_form.values()))
        count_value = list(pack.values()).count(True)

        payment.adviser = request.user.adviser

        # Variables para almacenar las cuotas y los pagos realizados
        paid_installments = []
        payments_list = []
        subtotal_amount = 0
        total_amount = 0
        discount = Decimal('0.00')
        show_payments = False
        if count_value == 0:
            show_payments = True
            if checked_discount:
                payment.amount = round_to_nearest_hundred(amount_paid * Decimal('0.95'))
                discount += round_to_nearest_hundred(amount_paid * Decimal('0.05'))
                payment.checked_discount = True
            else:
                payment.amount = amount_paid
            
            
            installments_caduced = [
                i for i in installments
                if i.is_caduced_installment and i.end_date and i.lastup and i.end_date.date() <= i.lastup
            ]
            if len(installments_caduced) > 0:
                installments_for_payment = installments_caduced
            else:
                installments_for_payment = installments
                
            payments = pay_installment(
                request,
                payment,
                installments_for_payment,
                abs(Decimal(form.cleaned_data["amount_paid"]))
            )

            # Guardamos las cuotas involucradas
            for payment in payments:
                subtotal_amount += payment.amount
                if payment.installment:
                    paid_installments.append(payment.installment)
                else:
                    paid_installments.append(payment.installment_ref)
            
            # Guardamos los pagos generados
            payments_list.extend(payments)
        else:
            for installment in pack.keys():
                if pack[installment]:
                    if checked_discount:
                        payment.amount = round_to_nearest_hundred(installment_amount * Decimal('0.95'))
                        discount += round_to_nearest_hundred(installment_amount * Decimal('0.05'))
                    else:
                        payment.amount = round_to_nearest_hundred(installment.amount)
                    subtotal_amount += installment.amount
                    installment.condition = 'Pagada'
                    installment.is_paid_installment = True
                    installment.payment_date = payment.payment_date
                    if installment.amount != installment.original_amount:
                        installment.amount = installment.original_amount
                    installment.save()
                    paid_installments.append(installment)
                    
                    credit = installment.credit
                    if credit.installments.filter(is_paid_installment=True).count() == credit.installments.count():
                        credit.condition = 'Pagado'
                        credit.payment_date = credit.installments.last().payment_date
                        credit.is_paid = True
                        credit.save()
                    new_payment = payment_create(payment, installment)
                    show_payments = True
                    payments_list.append(new_payment)
            interest = Interest.objects.first()
            points_per_installments = (
                interest.points_score_credits 
                if isinstance(installments, Installment) 
                else interest.points_score_refinancing
            )
            score = round((points_per_installments / installments_score) * count_value)
            client.score += score

            if (client.score + score) >= 1499:
                client.score = 1500
            client.save()
        discount = round_to_nearest_hundred(discount)
        for pay in payments_list:
            total_amount += pay.amount

        final_total = subtotal_amount - discount

        # Se obtiene la fecha del último pago realizado para formatearla
        if payments_list:
            last_payment = max(payments_list, key=lambda p: p.payment_date)
            payment_date_str = last_payment.payment_date.strftime('%d de %B de %Y')
        else:
            payment_date_str = payment.payment_date.strftime('%d de %B de %Y')

        # Opcional: Actualizar el concepto (detail) con la función de utilidad para cada cuota
        # Si cada pago está asociado a una cuota, se puede regenerar el concepto.
        print('CUOTAS', paid_installments)
        # Prepara el contexto para el recibo
        context = {
            'client': client,
            'dni': str(client.dni)[-6:], 
            'payments': payments_list,
            'installments': paid_installments,
            'payment_date': payment_date_str,
            'total_amount': final_total,
            'discount': discount,
            'subtotal_amount': subtotal_amount,    
            'amount_paid': amount_paid,            
            'payment_detail': payment.detail,  
            'receipt_number': payment.payment_date.strftime('%d%m%y%H%M'),    
            'checked_discount': checked_discount,
            'show_payments': show_payments,
            'is_get_receipt': False
        }

        return generate_pdf_receipt(request, context)

    return redirect('clients:detail', pk=client.pk)

# Descargar comprobante de pago
def get_receipt(request, pk, is_ref=False):
    """
    Vista para descargar el recibo asociado a una o más cuotas (Installment) dado su id.
    Si se han realizado pagos parciales, se acumulan todos los pagos asociados para reflejar
    el total abonado hasta el momento.
    """
    print(is_ref, type(is_ref)) 
    if is_ref == 'True':
        installment = get_object_or_404(InstallmentRefinancing, id=pk)
        payments = Payment.objects.filter(installment_ref=installment).order_by('payment_date')
    else:
        installment = get_object_or_404(Installment, id=pk)
        payments = Payment.objects.filter(installment=installment).order_by('payment_date')
    
    
    # Se utiliza la fecha del último pago para el recibo
    last_payment = payments.latest('payment_date') if payments.exists() else None
    payment_date_str = last_payment.payment_date.strftime('%d de %B de %Y') if last_payment else ""
    
    client = installment.credit.client
    discount = 0
    checked_discount = False
    discounted_amount = 0
    for payment in payments:
        if payment.checked_discount:
            checked_discount = True
            payment.discounted_amount = payment.amount * Decimal(0.05)
            discounted_amount += payment.discounted_amount

            discount = round_to_nearest_hundred(discounted_amount)
                
    discount = round_to_nearest_hundred(discount)
    subtotal = payments.aggregate(total=Sum('amount'))['total'] or 0

    if payments:
        receipt_number = payments[0].payment_date.strftime('%d%m%y%H%M')
    else:
        receipt_number = "N/A"  # o lo que quieras poner por defecto

    context = {
        'client': client,
        'dni': str(client.dni)[-6:], 
        'payments': payments,
        'installments': [installment],
        'payment_date': payment_date_str,
        'total_amount': installment.amount if installment.condition == 'Pagada' else subtotal - discount,           # Total acumulado de pagos (parciales o completos)
        'subtotal_amount': subtotal,  # Monto total que corresponde a la cuota
        'receipt_number': receipt_number,
        'checked_discount': checked_discount,
        'discount': discount,
        'is_get_receipt': True,
    }
    
    return generate_pdf_receipt(request, context)
