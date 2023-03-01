from datetime import date, datetime, timedelta
import decimal

from .models import Credit, InstallmentRefinancing

def refresh_condition_exp():
    if Credit.objects.exists():
        creditos_a_tiempo = Credit.objects.filter(condition = 'A Tiempo')       # TODOS LOS CREDITOS QUE 'ESTEN A TIEMPO'
        ###### __lt = (<) 'less-than sign' | __gt = (>) 'greater-than sign' and with e, like __lte or __gte, are 'less/greater-or equal-than sign'
        cred_with_vencidas = creditos_a_tiempo.filter(installment__end_date__date__lt=date.today())      ## OBTIENE TODOS LOS CREDITOS CON CUOTAS VENCIDAS (ej: 2/3 installments vencidas)
        installments_ref_vencidas = InstallmentRefinancing.objects.exclude(condition = 'Pagada').filter(end_date__date__lt=date.today())

        for installment_ven in cred_with_vencidas:                                                 
            for installment in installment_ven.installment.filter(end_date__date__lt=date.today()):
                if installment.condition != 'Refinanciada':  
                    installment.condition = 'Vencida'
                    if installment.lastup.date() != date.today(): 
                        dates = installment.lastup
                    else:
                        dates = installment.end_date
                    resto = (date.today() - dates.date()).days
                    installment.acc_int += resto*installment.amount*decimal.Decimal(0.02)
                    installment.lastup = datetime.today()
                    installment.save()
        
        for installment_ven in installments_ref_vencidas:                                                  
            installment_ven.condition = 'Vencida'
            if installment_ven.lastup.date() != date.today(): 
                dates = installment_ven.lastup
            else:
                dates = installment_ven.end_date
            resto = (date.today() - dates.date()).days
            installment_ven.acc_int += resto*installment_ven.amount*decimal.Decimal(0.02)
            installment_ven.lastup = datetime.today()
            installment_ven.save()

        for credito in creditos_a_tiempo:
            if credito.end_date.date() < date.today():
                credito.condition = 'Vencido'
                credito.save()                                                ## ACTUALIZACION DE condition DE CREDITO

            cred = credito.installment.filter(condition= 'Vencida')
            if cred.count() >= 2 and cred.end_date.date()+timedelta(days=10) < date.today():
                credito.condition = 'Legales'
                credito.save()

def refresh_condition_paid():
    credit_ok = Credit.objects.filter(is_paid_credit=False).filter(installment__is_paid_installment=True)

    for credit in credit_ok:
        if credit.installment.count() == credit.installment.filter(is_paid_installment=True).count():
            credit.is_paid_credit=True


def total_to_ref(amount, interest, pk, user, operation_mode):
    interest = int(interest)
    match(interest):
        case 25: installments = 3
        case 50: installments = 6
        case 75: installments = 9
        case 100: installments = 12
    
    interest = decimal.Decimal(float(interest/100) * float(amount))
    for i in range(installments):
        condition = 'A Tiempo'
        payment = None
        if i == 0:
            condition = 'Pagada'
            payment = operation_mode

        ref = InstallmentRefinancing.objects.create(
            amount=decimal.Decimal(amount/installments)+interest,
            installment_num = i+1,
            end_date = datetime.today() + (timedelta(days=30)*(i+1)),
            condition = condition,
            installment = pk,
            )
        if i == 0 :
            ref.payment = payment
            ref._adviser = user
            ref.save()

def all_properties_credit():
        return ["Monto solicitado", "Monto a devolver", "Numero de cuotas", "Monto de las cuotas", "Estado", "Cliente", "Asesor", "Fecha de registro", "Fecha de Finalizacion"]