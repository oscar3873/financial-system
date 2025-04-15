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

from credit.models import Credit, Refinancing, Installment
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
        installment_amount = round_to_nearest_hundred(refinancing.installments.first().amount)
        client = refinancing.installment_ref.last().credit.client
    except:
        credit = get_object_or_404(Credit, pk=pk)
        installments_score = credit.installments.all().count()
        installments = credit.installments.exclude(condition__in=['Refinanciada', 'Pagada'])
        installment_amount = round_to_nearest_hundred(credit.installments.first().amount)
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

        # Caso 1: Se han seleccionado cuotas completas (checkbox marcados)
        if count_value == 0:
            if checked_discount:
                payment.amount = round_to_nearest_hundred(installment_amount) * Decimal('0.95')
                discount += round_to_nearest_hundred(installment_amount) * Decimal('0.05')
            else:
                payment.amount = installment_amount
            subtotal_amount += installment_amount
            installments_caduced = [
                i for i in installments
                if i.is_caduced_installment and i.end_date and i.lastup and i.end_date.date() <= i.lastup
            ]
            payments = pay_installment(
                request,
                payment,
                installments_caduced,
                abs(Decimal(form.cleaned_data["amount_paid"]))
            )

            # Guardamos las cuotas involucradas
            paid_installments = list(installments_caduced)

            # Guardamos los pagos generados
            payments_list.extend(payments)
        else:
            for installment in pack.keys():
                if pack[installment]:
                    if checked_discount:
                        payment.amount = round_to_nearest_hundred(installment_amount) * Decimal('0.95')
                        discount += round_to_nearest_hundred(installment_amount) * Decimal('0.05')
                    else:
                        payment.amount = round_to_nearest_hundred(installment.amount)
                    subtotal_amount += installment.amount
                    installment.condition = 'Pagada'
                    installment.is_paid_installment = True
                    installment.payment_date = payment.payment_date
                    installment.save()
                    paid_installments.append(installment)
                    
                    credit = installment.credit
                    if credit.installments.filter(is_paid_installment=True).count() == credit.installments.count():
                        credit.condition = 'Pagado'
                        credit.payment_date = credit.installments.last().payment_date
                        credit.is_paid = True
                        credit.save()
                    new_payment = payment_create(payment, installment)
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

        for pay in payments_list:
            total_amount += pay.amount

        final_total = total_amount

        # Se obtiene la fecha del último pago realizado para formatearla
        if payments_list:
            last_payment = max(payments_list, key=lambda p: p.payment_date)
            payment_date_str = last_payment.payment_date.strftime('%d de %B de %Y')
        else:
            payment_date_str = payment.payment_date.strftime('%d de %B de %Y')

        # Opcional: Actualizar el concepto (detail) con la función de utilidad para cada cuota
        # Si cada pago está asociado a una cuota, se puede regenerar el concepto.
        print('CUOTAS', paid_installments)
        for pay in payments_list:
            # Obtiene la lista de pagos asociados a la cuota del pago actual (aquí se asume que es único)
            if pay.installment:
                concept = generate_concept_text(pay.installment, checked_discount, payments=[pay])
            else:
                concept = generate_concept_text(pay.installment_ref, checked_discount, payments=[pay])
            pay.detail = concept

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
        }

        return generate_pdf_receipt(request, context)

    return redirect('clients:detail', pk=client.pk)

# Descargar comprobante de pago
def get_receipt(request, pk):
    """
    Vista para descargar el recibo asociado a una o más cuotas (Installment) dado su id.
    Si se han realizado pagos parciales, se acumulan todos los pagos asociados para reflejar
    el total abonado hasta el momento.
    """
    installment = get_object_or_404(Installment, id=pk)
    
    # Recupera TODOS los pagos asociados a la cuota
    payments = Payment.objects.filter(installment=installment).order_by('payment_date')
    
    # Suma los montos pagados hasta el momento
    total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0

    # Acumula los detalles de cada pago (limpiando posibles datos extra)
    details = " | ".join([p.detail.split('-')[0] for p in payments if p.detail])
    
    # Se utiliza la fecha del último pago para el recibo
    last_payment = payments.latest('payment_date') if payments.exists() else None
    payment_date_str = last_payment.payment_date.strftime('%d de %B de %Y') if last_payment else ""
    
    # Recupera los datos del cliente a través del crédito de la cuota.
    client = installment.credit.client

    # Genera el concepto usando la función de utilidad.
    # Nota: se genera en función de la cuota y la suma de todos los pagos asociados.
    concept = generate_concept_text(installment, False, payments=payments)
    checked_discount = False
    # Actualiza el campo detail de cada Payment con el concepto generado.
    # Esto permitirá que en el template se muestre el concepto esperado.
    discount = 0
    for payment in payments:
        payment.detail = concept
        # Verifico si el pago es igual al 95% de la cuota
        if payment.amount == round_to_nearest_hundred(installment.amount) * Decimal('0.95'):
            checked_discount = True
            discount += round_to_nearest_hundred(installment.amount) * Decimal(0.05).quantize(Decimal('0.01'))
    
    if payments:
        receipt_number = payments[0].payment_date.strftime('%d%m%y%H%M')
    else:
        receipt_number = "N/A"  # o lo que quieras poner por defecto

    # Prepara el contexto para el template del recibo.
    context = {
        'client': client,
        'dni': str(client.dni)[-6:], 
        'payments': payments,
        'installments': [installment],
        'details': details,
        'payment_date': payment_date_str,
        'total_amount': total_paid,             # Total acumulado de pagos (parciales o completos)
        'subtotal_amount': installment.amount,  # Monto total que corresponde a la cuota
        'receipt_number': receipt_number,
        'checked_discount': checked_discount,
        'discount': discount
    }
    
    return generate_pdf_receipt(request, context)
