from django.contrib import admin

from guarantor.models import Guarantor, PhoneNumberGuarantor

# Register your models here.
class GuarantorAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 
        'last_name', 
        'email', 
        'credit', 
        'email', 
        'civil_status', 
        'dni', 
        'profession', 
        'address', 
        'job_address', 
        'created_at', 
        'updated_at'
    )

class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = (
        'phone_number_g', 
        'phone_type_g',
        'guarantor',
    )   

admin.site.register(Guarantor, GuarantorAdmin)
admin.site.register(PhoneNumberGuarantor, PhoneNumberAdmin)