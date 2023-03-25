from django import forms
from django.forms import TextInput
import django_filters
from django_filters import filters
from .models import Movement

OPERATION_CHOISE = (
    ('INGRESO', 'INGRESO'),
    ('EGRESO', 'EGRESO')
)

MONEY_TYPE = (
    ('PESOS', 'PESOS'),
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ('TRANSFER', 'TRANSFER'),
    ('CREDITO', 'CREDITO'),
    ('DEBITO', 'DEBITO'),
)

class ListingFilter(django_filters.FilterSet):
    
    amount = filters.RangeFilter(
        label="Monto",
        widget= django_filters.widgets.RangeWidget(attrs={'class': 'form-control w-40 m-auto','id': 'id_amount_filter'})
        )
    
    money_type = filters.ChoiceFilter(
        choices= MONEY_TYPE, 
        label="Divisa", 
        empty_label="Limpiar",
        widget=forms.Select(attrs={'class': 'form-control m-auto', 'id': 'id_money_type_filter'})
    )
    description = filters.CharFilter(
        label="Descripcion",
        lookup_expr="icontains",
        widget=TextInput(attrs={'class': 'form-control m-auto','id': 'id_description_filter'})
    )
    operation_mode = filters.ChoiceFilter(
        choices=OPERATION_CHOISE, 
        label="Operación", 
        empty_label="Limpiar",
        widget=forms.Select(attrs={'class': 'form-control m-auto','id': 'id_operation_mode_filter'}),
    )
    created_at = filters.DateFromToRangeFilter(
        label= "Desde - Hasta",
        widget= django_filters.widgets.RangeWidget(attrs={'type': 'date','class': 'form-control w-40 m-auto','id': 'id_created_at_filter'}),
        lookup_expr='icontains',
    )
    
    class Meta:
        model = Movement
        fields = ['amount', 'money_type', 'operation_mode', 'description', 'created_at', 'created_at']

class MoneyTypeFilter(django_filters.FilterSet):
    money_type = filters.ChoiceFilter(choices= MONEY_TYPE, label="Divisa", empty_label="Limpiar filtro")
    
    class Meta:
        model = Movement
        fields = {
            'money_type': ['exact']
        }


class AmountFilter(django_filters.FilterSet):
    amount = filters.RangeFilter(label="Monto")
    
    class Meta:
        model = Movement
        fields = ['amount']


class UserFilter(django_filters.FilterSet):
    user = filters.CharFilter(label="Por", field_name='user__username', lookup_expr='iexact')
    
    class Meta:
        model = Movement
        fields = {
            'user': ['exact']
        }
        
class DescriptionFilter(django_filters.FilterSet):
    description = filters.CharFilter(label="Descripción", lookup_expr="contains")
    
    class Meta:
        model = Movement
        fields = ['description']