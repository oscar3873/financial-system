from django.contrib import admin
from .models import Client, PhoneNumber
# Register your models here.
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name', 
        'address',
        'email', 
        'civil_status',
        'profession', 
        'dni', 
        'job_address',
        'created_at',
        'updated_at',
    )
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = (
        'phone_number', 
        'phone_type',
        'client',
    )   

admin.site.register(Client, ClientAdmin)
admin.site.register(PhoneNumber, PhoneNumberAdmin)