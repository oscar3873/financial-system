from django.contrib import admin

from .models import Warranty

# Register your models here.
class WarrantyAdmin(admin.ModelAdmin):
    list_display = (
        'article', 
        'brand', 
        'model', 
        'credit', 
        'state', 
        'accessories', 
        'purchase_papers',
        'created_at', 
        'updated_at'
    )

admin.site.register(Warranty, WarrantyAdmin)