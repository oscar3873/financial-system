from django.contrib import admin
from .models import CashRegister, Movement
# Register your models here.
class MovementAdmin(admin.ModelAdmin):
    list_display = (
        'amount',
        'cashregister',
        'operation_mode',
        'description',
        'money_type',
        'created_at',
        'updated_at',
    )

class MovementInline(admin.TabularInline):
    model = Movement
    
    fields = ['amount', 'operation_mode', 'money_type']

class CashRegisterAdmin(admin.ModelAdmin):
    list_display = (
        'total_balanceARS',
        'total_balanceUSD',
        'total_balanceEUR',
        'total_balanceTRANSFER',
        'total_balanceCREDITO',
        'total_balanceDEBITO',
    )
    inlines = [MovementInline]    

admin.site.register(CashRegister, CashRegisterAdmin)
admin.site.register(Movement, MovementAdmin)