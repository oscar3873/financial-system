from decimal import Decimal
from commissions.models import Commission, Interest

def commission_properties():
    return ["Monto", "Tipo de Comision","Fecha de Operacion", "Detalle", "Interes %"]


def comission_create(instance, adviser, detail):
    amount = instance.amount*Decimal(0.075)
    Commission.objects.create(
        adviser = adviser,
        amount = amount,
        operation_amount = instance.amount,
        type = 'REGISTRO',
        last_up = instance.start_date,
        detail = detail,
        ) 