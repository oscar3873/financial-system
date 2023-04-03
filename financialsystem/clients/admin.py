from django.contrib import admin
from .models import *
# Register your models here.
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
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
        'created_at'
    )  


admin.site.register(Client, ClientAdmin)
admin.site.register(PhoneNumberClient, PhoneNumberAdmin)