from django.contrib import admin
from .models import Commission

# Register your models here.
class NameAdmin(admin.ModelAdmin):
    list_display = ['created_at']

admin.site.register(Commission, NameAdmin)
