from django.contrib import admin
from .models import Payment

# Register your models here.
class PaymentAdmin(admin.ModelAdmin):
    fields = (
        'detail',
        'amount',
        'payment_date',
         )
    

admin.site.register(Payment, PaymentAdmin)