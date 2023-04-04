from django.forms import *
import django_filters
from django.db.models import Q

from django_filters import filters
from .models import Warranty

ARTICLE_STATE = (
    ('NUEVO','NUEVO'),
    ('USADO:COMO NUEVO', 'USADO:COMO NUEVO'),
    ('USADO:MUY BUENO', 'USADO:MUY BUENO'),
    ('USADO:BUENO', 'USADO:BUENO'),
    ('USADO:ACEPTABLE', 'USADO:ACEPTABLE'),
    ('USADO:REACONDICIONADO', 'USADO:REACONDICIONADO'),
    ('USADO:MUCHO USO', 'USADO:MUCHO USO'),
)


class ListingFilter(django_filters.FilterSet):
    article = filters.CharFilter(
        label="Articulo", 
        lookup_expr="icontains",
        widget=TextInput(attrs={'class': 'form-control'})
        )

    model = filters.CharFilter(
        label="Modelo", 
        lookup_expr="icontains",
        widget=TextInput(attrs={'class': 'form-control'})
        )

    brand = filters.CharFilter(
        label="Marca", 
        lookup_expr="icontains",
        widget=TextInput(attrs={'class': 'form-control'})
        )

    accessories = filters.CharFilter(
        label="Accesorios", 
        lookup_expr="icontains",
        widget=TextInput(attrs={'class': 'form-control'})
        )

    state = filters.ChoiceFilter(
        choices=ARTICLE_STATE, 
        label="Estado", 
        empty_label="Limpiar filtro",
        widget=Select(attrs={'class': 'form-control'})
        )

    purchase_papers = filters.BooleanFilter(
        label="Papeles de compra", 
        lookup_expr="exact",
        widget= Select(
            attrs={'class': 'form-control'}, 
            choices=[(True,"SI"),(False,"NO")]
            )
        )

    created_at = filters.DateFromToRangeFilter(
        label= "Desde - Hasta",
        widget= django_filters.widgets.RangeWidget(attrs={'type': 'date'}),
        lookup_expr='icontains',
    )
    client = django_filters.CharFilter(
        label="Cliente asociado",
        lookup_expr="icontains",
        method="name_of_credit_client",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Cliente asociado'})
    )  
    
    def name_of_credit_client(self, queryset, name, value):
        return queryset.filter(Q(credit__client__first_name__icontains=value) | Q(credit__client__last_name__icontains=value))
    

    class Meta:
        model = Warranty
        fields = ['article', 'model', 'brand', 'accessories', 'state', 'client','created_at', 'created_at']