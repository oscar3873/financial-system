from django.contrib import admin
from .models import Adviser, Comission

# Register your models here.
class NameAdmin(admin.ModelAdmin):
    list_display = ('user','created_at')

admin.site.register(Adviser, NameAdmin)
admin.site.register(Comission)
