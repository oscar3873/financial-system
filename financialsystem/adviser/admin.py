from django.contrib import admin
from .models import Adviser

# Register your models here.
class NameAdmin(admin.ModelAdmin):
    list_display = ('user','created_at')

admin.site.register(Adviser, NameAdmin)