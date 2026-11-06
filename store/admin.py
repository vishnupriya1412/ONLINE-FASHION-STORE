from django.contrib import admin
from .models import Product
from .models import Order, OrderItem

admin.site.register(Order)
admin.site.register(OrderItem)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "created_at")
    list_filter = ("category",)
    search_fields = ("name", "description")
