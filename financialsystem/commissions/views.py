from django.shortcuts import redirect, render
from django.contrib import messages

from commissions.forms import SettingsInterestForm
from commissions.models import Interest
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required(login_url="/accounts/login/")
def setting_parameters(request):
    if request.method == 'POST':
        form = SettingsInterestForm(request.POST, instance=Interest.objects.first())
        if form.is_valid():
            form.save()
            messages.success(request,"Configuracion completada con exito!","success")
        else:
            print(form.errors)
    
    return redirect('advisers:list')