from django.forms import DateInput
import django_filters
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
    article = filters.CharFilter(label="Articulo", lookup_expr="icontains")
    model = filters.CharFilter(label="Modelo", lookup_expr="icontains")
    brand = filters.CharFilter(label="Marca", lookup_expr="icontains")
    accessories = filters.CharFilter(label="Accesorios", lookup_expr="icontains")
    state = filters.ChoiceFilter(choices=ARTICLE_STATE, label="Estado", empty_label="Limpiar filtro")
    purchase_papers = filters.BooleanFilter(label="Papeles de compra", lookup_expr="exact")
    client = filters.CharFilter(label="Cliente", lookup_expr="exact")
    created_at = filters.DateFromToRangeFilter(
        label= "Desde - Hasta",
        widget= django_filters.widgets.RangeWidget(attrs={'type': 'date'}),
        lookup_expr='icontains',
    )
    
    class Meta:
        model = Warranty
        fields = ['article', 'model', 'brand', 'accessories', 'state', 'client','created_at', 'created_at']