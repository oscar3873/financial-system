from decimal import Decimal
from commissions.models import Commission, Interest

def commission_properties():
    return ["Monto", "Tipo de Comision","Fecha de Operacion", "Detalle", "Interes %"]


def comission_create(instance, adviser, detail):
    amount = instance.amount*Interest.objects.first().interest_register/Decimal(100)
    Commission.objects.create(
        adviser = adviser,
        amount = Decimal(amount),
        operation_amount = instance.amount,
        type = 'REGISTRO',
        last_up = instance.start_date,
        detail = detail,
        ) 