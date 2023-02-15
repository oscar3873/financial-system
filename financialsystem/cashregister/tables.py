import django_tables2 as tables
from .models import Movement

class MovementTable(tables.Table):
    class Meta:
        model = Movement
        template_name = "django_table2/bootstrap.html"
        fields = ("amount", "operation_mode", "description", "money_type", "created_at")