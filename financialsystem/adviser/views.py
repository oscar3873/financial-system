from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin
from .models import Adviser

# Create your views here.
class AdviserListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Adviser
    group_required = "admin_group"
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def handle_no_permission(self, request):
        return redirect("/")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["count_advisers"] = Adviser.objects.all().count()
        context["advisers"] = Adviser.objects.all()
        return context
    

class AdviserDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = Adviser
    
    group_required = "admin_group"
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def handle_no_permission(self, request):
        return redirect("/")
    
    def get_object(self):
        return get_object_or_404(Adviser, id=self.kwargs['pk'])

class AdviserUpdateView(UpdateView):
    pass

class AdviserDeleteView(DeleteView):
    pass

class AdviserCreateView(CreateView):
    pass