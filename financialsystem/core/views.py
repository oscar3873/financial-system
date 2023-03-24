from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from note.models import Note
from credit.utils import refresh_condition
from cashregister.models import CashRegister, Movement
from cashregister.utils import create_cashregister

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
        """
        Extrae los datos de los modelos necesarios que se encuentran en la base de datos para usarlo en el contexto.
        """
        refresh_condition()
        create_cashregister()
        context = super().get_context_data(**kwargs)
        Caja = CashRegister.objects.get_or_create()
        context["cashregister"] = Caja[0]
        context["notes"] = Note.objects.all().order_by("-created_at")[0:4]
        context["movements"] = Movement.objects.all().filter(user = self.request.user.adviser).order_by("-created_at")[0:4]
        return context