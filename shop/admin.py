from django.contrib import admin
from . import models 
# Register your models here.

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug' : ('name',)}
    


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'stock', 'available', 'created_at', 'updated_at']
    list_filter = ['available', 'category']
    search_fields = ['name']
    prepopulated_fields = {'slug' : ('name', )}



# Fixed: Indentation error corrected
admin.site.register(models.Rating)
admin.site.register(models.Cart)
admin.site.register(models.CartItem)
admin.site.register(models.Order)
admin.site.register(models.OrderItem)