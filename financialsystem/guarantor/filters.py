from django.forms import DateInput
import django_filters
from django_filters import filters
from .models import Guarantor

CivilStatus = (
    ('S','Soltero'),
    ('C', 'Casado'),
    ('V', 'Viudo'),
    ('D', 'Divorciado')
    )


class ListingFilter(django_filters.FilterSet):
    dni = filters.CharFilter(label="DNI", lookup_expr="exact")
    client = filters.CharFilter(label="Cliente")
    created_at = filters.DateFromToRangeFilter(
        label= "Desde - Hasta",
        widget= django_filters.widgets.RangeWidget(attrs={'type': 'date'}),
        lookup_expr='icontains',
    )
    
    class Meta:
        model = Guarantor
        fields = ['dni', 'client', 'created_at', 'created_at']