from django.contrib import admin
from .models import Client, PhoneNumberClient
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
        'score',
        'score_label',
        'job_address',
        'created_at',
        'updated_at',
    )
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = (
        'phone_number_c', 
        'phone_type_c',
        'client',
    )   

admin.site.register(Client, ClientAdmin)
admin.site.register(PhoneNumberClient, PhoneNumberAdmin)