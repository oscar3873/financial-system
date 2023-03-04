from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from braces.views import GroupRequiredMixin
from .models import Adviser, Comission
from .utils import commission_properties
from cashregister.models import CashRegister, Movement

# Create your views here.
class AdviserListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Adviser
    group_required = "admin_group"
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def handle_no_permission(self):
        return redirect("/accounts/login/")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["count_advisers"] = Adviser.objects.count()
        context["advisers"] = Adviser.objects.all()
        return context
    

class AdviserDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = Adviser
    
    group_required = "admin_group"
    #CARACTERISTICAS DEL LOGINREQUIREDMIXIN
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def handle_no_permission(self):
        return redirect("/")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commissions"] = Comission.objects.filter(adviser=self.get_object())
        context["properties"] = commission_properties()
        return context

    def get_object(self):
        return get_object_or_404(Adviser, id=self.kwargs['pk'])

#----------------------------------------------------------------
@login_required(login_url="/accounts/login/")
def pay_commission(request,pk):
    try:
        commission = Comission.objects.get(id=pk)
        commission.is_paid = True
        commission.save()
    except Comission.DoesNotExist:
        return redirect('advisers:detail', pk=commission.adviser.id)

    create_movement(commission)

    return redirect('advisers:detail', pk=commission.adviser.id)


class AdviserUpdateView(UpdateView):
    model = Adviser
    

class AdviserDeleteView(DeleteView):
    pass


def create_movement(commission):
    Movement.objects.create(
            user = commission.adviser,
            amount = commission.amount,
            cashregister = CashRegister.objects.last(),
            operation_mode = 'EGRESO',
            description = 'COMISION %s - %s' % (commission.adviser, commission.type),
            money_type= commission.money_type
        )