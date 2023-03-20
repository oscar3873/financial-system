import django_filters
from .models import Guarantor
from django.db.models import Q
from django.forms import TextInput

class ListingFilter(django_filters.FilterSet):
    """
    Filtrador de Garante.
    """
    dni = django_filters.NumberFilter(
        label="DNI",
        lookup_expr="iexact",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI'})
    )
    first_name_or_last_name = django_filters.CharFilter(
        label="Nombre o apellido",
        lookup_expr="icontains",
        method="filter_name_or_lastname",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre o Apellido'})
    )
    client = django_filters.CharFilter(
        label="Cliente asociado",
        lookup_expr="icontains",
        method="name_of_credit_client",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Cliente asociado'})
    )

    def filter_name_or_lastname(self, queryset, name, value):
        return queryset.filter(Q(first_name__icontains=value) | Q(last_name__icontains=value))
    
    def name_of_credit_client(self, queryset, name, value):
        return queryset.filter(Q(credit__client__first_name__icontains=value) | Q(credit__client__last_name__icontains=value))
    
    class Meta:
        model = Guarantor
        fields = ['dni', 'first_name', 'last_name', 'first_name_or_last_name', 'client']