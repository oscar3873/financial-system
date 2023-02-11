from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django import forms

from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

from django.urls import reverse_lazy

#CRUD MOVEMENT
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from .models import Movement, CashRegister
from .forms import MovementForm
from django.views.generic.edit import FormView

# Create your views here.
class CashRegisterListView(LoginRequiredMixin, FormView, ListView):
    
    model = CashRegister
    second_model = Movement
    form_class = MovementForm
    template_name = 'cashregister/cashregister.html'
    
    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context["cashregister"] = self.model.objects.all()[0]
        context["movements"] = self.second_model.objects.all().order_by('-created_at')[0:4]
        return context
    
    def form_valid(self, form):
        
        if self.request.method == 'POST':
            print(form.cleaned_data)
            form.save()
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return  reverse_lazy('cashregister:home')
    
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

class MovementListView(LoginRequiredMixin, ListView):
    model = Movement
    template_name = "cashregister/movement_list.html"
    paginate_by = 4
    ordering = ['-created_at']
    
    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context["count_movements"] = self.model.objects.all().count()
        context["movements"] = self.model
        #VALIDACION DE EXISTENCIA PARA AL MENOS UN CLIENTE
        if self.model.objects.all().count() > 0:
            context["properties"] = self.model.objects.all()[0].all_properties()
        
        return context

class MovementDetailView(LoginRequiredMixin, DetailView):
    model = Movement
    template_name = 'cashregister/movement_detail.html'
    
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_object(self):
        return get_object_or_404(Movement, id=self.kwargs['pk'])

#BORRADO DE UN MOVIMIENTO
#------------------------------------------------------------------
class MovementDeleteView(DeleteView):
    model = Movement
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Movimiento eliminado correctamente', "danger")
        return  reverse_lazy('cashregister:list')

#ACTUALIZACION DE UN MOVIMIENTO
#------------------------------------------------------------------
class MovementUpdateView(UpdateView):
    model = Movement
    form_class = MovementForm
    template_name_suffix = '_update_form'
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Movimiento actualizado satisfactoriamente', "info")
        return  reverse_lazy('cashregister:list')