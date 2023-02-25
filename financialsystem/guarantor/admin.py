from django.contrib import admin

from guarantor.models import Guarantor, PhoneNumber

# Register your models here.
class GuarantorAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 
        'last_name', 
        'email', 
        'client', 
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
        'phone_number', 
        'phone_type',
        'guarantor',
    )   

admin.site.register(Guarantor, GuarantorAdmin)
admin.site.register(PhoneNumber, PhoneNumberAdmin)