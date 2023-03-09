from django.contrib import admin

from .models import Warranty, Sell

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

class SelldAdmin(admin.ModelAdmin):
    list_display = (
        'amount', 
        'payment_method', 
        'adviser', 
        'article', 
        'detail', 
        'created_at', 
        'updated_at'
    )

admin.site.register(Warranty, WarrantyAdmin)
admin.site.register(Sell, SelldAdmin)