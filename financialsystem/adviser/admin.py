from django.contrib import admin
from .models import Adviser

# Register your models here.
class NameAdmin(admin.ModelAdmin):
    list_display = ('user','created_at', 'avatar')

admin.site.register(Adviser, NameAdmin)
# admin.site.register(Commission, NameAdmin)
