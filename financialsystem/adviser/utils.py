from decimal import Decimal
from .models import Comission

def commission_properties():
    return ["Monto", "Tipo de Comision","Fecha de Operacion", "Detalle", "Interes %"]


def comission_create(instance, adviser, detail):
    amount = instance.amount*Decimal(0.075)
    Comission.objects.create(
        adviser = adviser,
        interest = Decimal(7.5),
        amount = amount,
        operation_amount = instance.amount,
        type = 'REGISTRO',
        last_up = instance.start_date,
        detail = detail,
        ) 