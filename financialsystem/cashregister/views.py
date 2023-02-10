from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from .models import Movement, CashRegister

# Create your views here.
class CashRegisterListView(LoginRequiredMixin, ListView):
    model = CashRegister
    second_model = Movement
    template_name = 'cashregister/cashregister.html'
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context["cashregister"] = self.model.objects.all()[0]
        context["movements"] = self.second_model.objects.all()
        return context
    
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
class MovementDetailView(LoginRequiredMixin, DetailView):
    model = Movement
    template_name = 'cashregister/movement_detail.html'
    
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_object(self):
        return get_object_or_404(Movement, id=self.kwargs['id'])
    
class MovementCreateView(CreateView):
    model = Movement
    fields = ['amount', 'description', 'operation_mode', 'money_type']
    template_name = 'cashregister/movement_form.html'