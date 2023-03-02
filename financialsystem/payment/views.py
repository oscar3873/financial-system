from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

from django.urls import reverse, reverse_lazy

#CRUD Payment
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from credit.models import Credit
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

#CREACION DE UNA NOTA
class PaymentCreateView(CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = "payment/payment_form.html"
    
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     self.objet = get_object_or_404(Credit, pk = self.kwargs["pk"])
    #     excludes = ['Refinanciada', 'Pagada']
    #     self.installments = self.objet.installment.exclude(condition__in=excludes)
    #     kwargs["installments"] = self.installments
    #     return kwargs
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Nota creada correctamente', "success")
        print(self.objet, self.objet.client)
        return  reverse_lazy('clients:detail', kwargs={'pk': self.objet.client.id})
    
    def form_valid(self, form):
        installments_credit = list(self.installments.all())
        checkboxs_by_form = {key: True for key, value in self.request.POST.items() if key.startswith('Cuota')}

        pack = dict(zip(installments_credit, checkboxs_by_form.values()))
        print(pack)
        if form.is_valid():
            payment = form.save(commit=False)
            payment._user = self.request.user
            for installment in pack.keys():
                installment.condition = 'Pagada'
                installment.is_paid_installment = True
                payment.installment = installment
                payment.save()
                installment.save()
            
        return super(PaymentCreateView, self).form_valid(form)


def make_payment_installment(request,pk):
    credit = get_object_or_404(Credit, pk = pk)

    excludes = ['Refinanciada', 'Pagada']
    installments = credit.installment.exclude(condition__in=excludes)
    
    form = PaymentForm(installments, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            installments_credit = list(installments.all())
            checkboxs_by_form = {key: True for key, value in request.POST.items() if key.startswith('Cuota')}
            pack = dict(zip(installments_credit, checkboxs_by_form.values()))
            count_value = list(pack.values()).count(True)
            print(count_value)
            payment = form.save(commit=False)
            amount = Decimal(payment.amount / count_value)
            print('########################AMOUNT######################')
            for installment in pack.keys():
                installment.condition = 'Pagada'
                installment.is_paid_installment = True
                installment.save()
                print('##############################################')
                Payment.objects.create(
                    amount=amount,
                    paid_date=payment.paid_date,
                    installment = installment,
                    adviser=request.user.adviser,
                    payment_method = payment.payment_method,
                    detail = 'COBRO CUOTA %s - CLIENTE %s - ASESOR %s' % (installment.installment_number, installment.credit.client, request.user.adviser)
                )
                
        return reverse_lazy('clients:detail', kwargs={'pk':credit.client.pk} )
    
    return render(request, 'payment/payment_form.html', {'form':form})



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