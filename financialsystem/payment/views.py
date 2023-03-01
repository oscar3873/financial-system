from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

from django.urls import reverse_lazy

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
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.objet = get_object_or_404(Credit, pk = self.kwargs["pk"])
        excludes = ['Refinanciada', 'Pagada']
        self.installments = self.objet.installment.exclude(condition__in=excludes)
        kwargs["installments"] = self.installments
        return kwargs
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Nota creada correctamente', "success")
        return  reverse_lazy('clients:detail', pk=self.objet.client.pk)
    
    def form_valid(self, form):
        installments = list(self.installments.all())
        cuotas = {key: True for key, value in self.request.POST.items() if key.startswith('Cuota')}

        pack = dict(zip(installments, cuotas.values()))
        
        if form.is_valid():
            payment = form.save(commit=False)
            payment._user = self.request.user
            for payed in pack.keys():
                payed.condition = 'Pagada'
                payed.is_paid_installment = True
                payed.save()
                payment.installment = payed
                payment.save()
            
        return super().form_valid(form)

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