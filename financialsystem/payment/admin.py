from django.contrib import admin
from .models import Payment

# Register your models here.
class PaymentAdmin(admin.ModelAdmin):
    fields = (
        'detail',
         'installment',
         'installment_ref',
         'is_refinancing_pay',
         'amount',
         'payment_date',
         )
    

admin.site.register(Payment, PaymentAdmin)