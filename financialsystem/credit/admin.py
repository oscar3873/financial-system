from django.contrib import admin
from .models import Credit, Installment, Refinancing, InstallmentRefinancing

# Register your models here.
class CreditAdmin(admin.ModelAdmin):
    list_display = (
        'client',
        'amount',
        'installment_num', 
        'credit_interest',
        'credit_repayment_amount', 
        'is_paid_credit',
        'created_at', 
        'updated_at'
    )

class InstallmentAdmin(admin.ModelAdmin):
    list_display = (
        'credit',
        'installment_number', 
        'amount', 
        'payment_date',
        'is_caduced_installment', 
        'is_paid_installment', 
        'is_refinancing_installment', 
        'created_at', 
        'updated_at'
    )

class RefinancingAdmin(admin.ModelAdmin):
    list_display = (
            'installment',
            'is_paid_refinancing',
            'refinancing_interest', 
            'amount', 
            'refinancing_repayment_amount', 
            'installment_num_refinancing',
            'created_at',
            'updated_at'
    )
    
    
class InstallmentRefinancingAdmin(admin.ModelAdmin):
    list_display = (
            'refinancing',
            'installment_number',
            'amount', 
            'payment_date', 
            'is_caduced_installment', 
            'is_paid_installment', 
            'created_at', 
            'updated_at'
    )

admin.site.register(Credit, CreditAdmin)
admin.site.register(Installment, InstallmentAdmin)
admin.site.register(Refinancing, RefinancingAdmin)
admin.site.register(InstallmentRefinancing, InstallmentRefinancingAdmin)