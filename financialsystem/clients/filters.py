import django_filters
from .models import Client

class ClientFilter(django_filters.FilterSet):
    dni = django_filters.NumberFilter(lookup_expr="iexact")
    
    class Meta:
        model = Client
        fields = ['dni']