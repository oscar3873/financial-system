import django_tables2 as tables
from .models import Movement

class MovementTable(tables.Table):
    amount = tables.Column(verbose_name="Monto")
    operation_mode = tables.Column(verbose_name="Operación")
    description = tables.Column(verbose_name="Descripción")
    money_type = tables.Column(verbose_name="Divisa")
    created_at = tables.Column(verbose_name="Fecha de Realización")
    user = tables.Column(verbose_name="Por")
    Acciones = tables.Column(
    verbose_name="Acciones",
    attrs={"a":"class= btn"}
    )

    class Meta:
        attrs = {"class": "table table-striped table-hover"}
        model = Movement
        template_name = "django_tables2/bootstrap.html"
        fields = ("amount", "operation_mode", "description", "money_type", "created_at", "user")