from datetime import datetime
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from django.urls import reverse, reverse_lazy

#CRUD Payment
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from credit.models import Credit
from credit.models import Refinancing
from .utils import payment_create
from .models import Payment
from .forms import PaymentForm

# Create your views here.
class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = "payment/payment_list.html"
    paginate_by = 6
    ordering = ['-created_at']
    
    def get_context_data(self, **kwargs):
        
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context["count_payments"] = self.model.objects.all().count()
        context["payments"] = self.model.objects.all()
        #VALIDACION DE EXISTENCIA PARA AL MENOS UN CLIENTE
        # if self.model.objects.all().count() > 0:
        #     context["properties"] = self.model.objects.all()[0].all_properties()
        
        return context

#BORRADO DE UNA NOTA
#------------------------------------------------------------------
class PaymentDeleteView(DeleteView):
    model = Payment
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Nota eliminada correctamente', "danger")
        return  reverse_lazy('payments:list')

#ACTUALIZACION DE UN MOVIMIENTO
#------------------------------------------------------------------
class PaymentUpdateView(UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name_suffix = '_update_form'
    
    def get_form_kwargs(self):
        
        kwargs = super(PaymentUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Nota actualizada satisfactoriamente', "info")
        return  reverse_lazy('payments:list')
    
#REALIZAR DE UN PAGO
#------------------------------------------------------------------
@login_required(login_url="/accounts/login/")
def make_payment_installment_ref(request, pk):
    refinancing = get_object_or_404(Refinancing, pk=pk)
    installments = refinancing.installment_refinancing.exclude(condition='Pagada')
    form = PaymentForm(installments, request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        installment_ref = list(installments.all())
        checkboxs_by_form = {key: value for key, value in form.cleaned_data.items() if key.startswith('Cuota') and value}
        pack = dict(zip(installment_ref, checkboxs_by_form.values()))
        count_value = list(pack.values()).count(True)
        payment = form.save(commit=False)

        payment.amount = Decimal(payment.amount / count_value)
        payment._adviser = request.user.adviser

        for installment in pack.keys():
            installment.condition = 'Pagada'
            installment.is_paid_installment = True
            installment.payment_date = payment.payment_date
            installment.save()
            payment_create(payment, installment)
        return redirect('clients:list')
    
    return render(request, 'payment/payment_form.html', {'form': form})

#REALIZAR DE UN PAGO
#------------------------------------------------------------------
def make_payment_installment(request, pk):
    credit = get_object_or_404(Credit, pk=pk)
    installments = credit.installment.exclude(condition__in=['Refinanciada', 'Pagada'])
    form = PaymentForm(installments, request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        installments_credit = list(installments.all())
        checkboxs_by_form = {key: value for key, value in form.cleaned_data.items() if key.startswith('Cuota') and value}
        pack = dict(zip(installments_credit, checkboxs_by_form.values()))
        count_value = list(pack.values()).count(True)
        
        print(pack)
        payment = form.save(commit=False)
        payment.amount = Decimal(payment.amount / count_value)
        payment._adviser = request.user.adviser

        for installment in pack.keys():
            installment.condition = 'Pagada'
            installment.is_paid_installment = True
            installment.payment_date = payment.payment_date
            installment.save()
            payment_create(payment, installment)
        return redirect('clients:detail', pk=credit.client.pk)
    
    return render(request, 'payment/payment_form.html', {'form': form})