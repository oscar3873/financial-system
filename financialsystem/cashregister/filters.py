from django.forms import DateInput
import django_filters
from django_filters import filters
from .models import Movement

OPERATION_CHOISE = (
    ('Ingreso', 'Ingreso'),
    ('Egreso', 'Egreso')
)

MONEY_TYPE = (
    ('PESO', 'PESO'),
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ('TRANSFER', 'TRANSFER'),
    ('CREDITO', 'CREDITO'),
    ('DEBITO', 'DEBITO'),
)

class ListingFilter(django_filters.FilterSet):
    
    description = filters.CharFilter(label="Descripción", lookup_expr="contains")
    operation_mode = filters.ChoiceFilter(choices=OPERATION_CHOISE, label="Tipo de Operación", empty_label="Limpiar filtro")
    created_at = filters.DateFromToRangeFilter(
        label= "Desde - Hasta",
        widget= django_filters.widgets.RangeWidget(attrs={'type': 'date'}),
        lookup_expr='icontains',
    )
    
    class Meta:
        model = Movement
        fields = ['description', 'operation_mode', 'created_at', 'created_at']

class MoneyTypeFilter(django_filters.FilterSet):
    
    money_type = filters.ChoiceFilter(choices= MONEY_TYPE, label="Divisa", empty_label="Limpiar filtro")
    
    class Meta:
        model = Movement
        fields = {
            'money_type': ['exact']
        }

class AmountFilter(django_filters.FilterSet):
    
    amount = filters.CharFilter(label="Monto")
    
    class Meta:
        model = Movement
        fields = {
            'amount': ['exact']
        }

class UserFilter(django_filters.FilterSet):
    
    user = filters.CharFilter(label="Por", field_name='user__username', lookup_expr='iexact')
    
    class Meta:
        model = Movement
        fields = {
            'user': ['exact']
        }