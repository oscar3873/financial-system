from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import UpdateView, DeleteView, CreateView

from django.urls import reverse_lazy

from django.contrib import messages 

from .forms import CreditForm

from .models import Credit

# Create your views here.
class CreditListView(ListView):
    model = Credit
    
class CreditDetailView(DetailView):
    model = Credit
    
class CreditCreateView(CreateView):
    model = Credit
    form_class = CreditForm
    
    def get_success_url(self) -> str:
        messages.success(self.request, 'Credito creado correctamente', "success")
        return  reverse_lazy('notes:list')

class CreditUpdateView(UpdateView):
    model = Credit
    
class CreditDeleteView(DeleteView):
    model = Credit

