from cashregister.models import CashRegister, Movement

def commission_properties():
    return ["Monto", "Tipo de Comision","Fecha de Operacion", "Detalle", "Interes %"]

def create_movement(commission):
    '''Crea un nuevo objeto Movement y lo guarda en la base de datos.'''
    mov = Movement.objects.create(
            user = commission.adviser,
            amount = commission.amount,
            cashregister = CashRegister.objects.last(),
            operation_mode = 'EGRESO',
            description = 'COMISION %s - %s' % (commission.adviser, commission.type),
            money_type= commission.money_type
        )
    commission.id_mov = mov.id
    commission.save()
