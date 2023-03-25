"""financialsystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from clients.urls import clients_patterns
from cashregister.urls import cashregister_patterns
from note.urls import note_patterns
from adviser.urls import advisers_patterns
from credit.urls import credits_patterns
from guarantor.urls import guarantor_patterns
from warranty.urls import warranty_patterns
from payment.urls import payment_patterns
from commissions.urls import commission_patterns

urlpatterns = [
    # Paths de Nucleo del proyecto
    path("", include("core.urls")),
    path("admin/", admin.site.urls),
    # Paths de Auth
    path('accounts/', include('django.contrib.auth.urls')),
    path("accounts/", include("registration.urls")),
    path("clients/", include(clients_patterns)),
    path("cashregister/", include(cashregister_patterns)),
    path("notes/", include(note_patterns)),
    path("asesors/", include(advisers_patterns)),
    path("credits/", include(credits_patterns)),
    path("guarantors/", include(guarantor_patterns)),
    path("warrantys/", include(warranty_patterns)),
    path("payments/", include(payment_patterns)),
    path("commissions/", include(commission_patterns)),
]
