from django.forms import DateInput
import django_filters
from django_filters import filters
from .models import Guarantor


class ListingFilter(django_filters.FilterSet):
    """
    Filtrador Garante.
    """
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