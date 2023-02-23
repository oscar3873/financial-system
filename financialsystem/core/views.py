from django.shortcuts import render
from django.views.generic.base import TemplateView
from note.models import Note
from credit.models import Installment
from cashregister.models import CashRegister, Movement
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"
    modelNote = Note
    modelCashregister = CashRegister
    modelMovement = Movement
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cashregister"] = CashRegister.objects.last()
        context["notes"] = Note.objects.all().filter(user = self.request.user).order_by("-created_at")[0:4]
        context["movements"] = Movement.objects.all().filter(user = self.request.user).order_by("-created_at")[0:4]
        context['next_maturities'] = Installment.objects.filter(credit__client__adviser= self.request.user).filter(condition='A Tiempo')[0:4]
        return context