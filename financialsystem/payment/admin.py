from django.contrib import admin
from .models import Payment

# Register your models here.
class PaymentAdmin(admin.ModelAdmin):
    fields = ('detaill', 'installment', 'refinancing', 'is_refinancing_pay')
    

admin.site.register(Payment, PaymentAdmin)