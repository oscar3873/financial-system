from django.contrib import admin
from .models import Client, PhoneNumber
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name', 
        'address',
        'email', 
        'civil_status',
        'profession', 
        'dni', 
        'get_phone_numbers',
        'job_address',
    )
    
    def get_phone_numbers(self, obj):
        return "\n, ".join([p.phone_number for p in obj.phone_numbers.all()])

class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'phone_type')   

admin.site.register(Client, UserAdmin)
admin.site.register(PhoneNumber, PhoneNumberAdmin)