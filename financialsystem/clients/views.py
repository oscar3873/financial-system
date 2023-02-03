from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Client
# Create your views here.
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    
    def get_object(self):
        return get_object_or_404(Client, id=self.kwargs['id'])