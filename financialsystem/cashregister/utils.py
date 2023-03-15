from cashregister.models import Movement, CashRegister
from adviser.utils import comission_create


def all_properties_mov():
    return ["Monto","Operacion","Descripcion","Divisa","Fecha","Por"]


def create_movement(instance, adviser):
    mov = Movement.objects.create(
        user = adviser,
        amount = instance.amount,
        cashregister = CashRegister.objects.last(),
        operation_mode = 'EGRESO',
        description = 'CREDITO OTORGADO A %s - CUOTAS: %s' % (instance.client, instance.installment_num),
        money_type = 'PESOS',
        )
    comission_create(instance, adviser, detail=mov.description)
    return mov
