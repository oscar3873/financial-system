import django_filters
from .models import Client
from django.db.models import Q
from django.forms import TextInput

class ListingFilter(django_filters.FilterSet):
    """
    Filtrador de Cliente.
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

    def filter_name_or_lastname(self, queryset, name, value):
        search_terms = value.split()

        for term in search_terms:
            q_objects = Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(dni__icontains=term)
            queryset = queryset.filter(q_objects)

        return queryset.distinct()

    
    class Meta:
        model = Client
        fields = ['dni', 'first_name', 'last_name', 'first_name_or_last_name']
