from django.contrib import admin
from .models import Payment

# Register your models here.
class PaymentAdmin(admin.ModelAdmin):
    fields = (
        'detail',
        'amount',
        'payment_date',
        'installment',
        'mov',
         )
    

admin.site.register(Payment, PaymentAdmin)