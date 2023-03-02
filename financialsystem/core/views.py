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
        Caja = CashRegister.objects.get_or_create()
        context["cashregister"] = Caja[0]
        context["notes"] = Note.objects.all().filter(user = self.request.user.adviser).order_by("-created_at")[0:4]
        context["movements"] = Movement.objects.all().filter(user = self.request.user.adviser).order_by("-created_at")[0:4]
        return context