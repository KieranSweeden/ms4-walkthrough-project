from django.contrib import admin
from .models import Product, Category

# Register your models here.

class ProductAdmin(admin.ModelAdmin):

    # Change list display in admin to
    # friendly names instead of programmatic ones
    list_display = (
        "sku",
        "name",
        "category",
        "price",
        "rating",
        "image"
    )

    # sort products by sku using ordering attribute
    # has to be tuple despite giving one parameter
    # adding a - before sku reverses it
    ordering = ("sku",)

class CategoryAdmin(admin.ModelAdmin):

    # Change list display in admin to
    # friendly names instead of programmatic ones
    list_display = (
        "friendly_name",
        "name"
    )

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)