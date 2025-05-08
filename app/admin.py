from django.contrib import admin
from .models import *


# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'phone')
    search_fields = ['name', 'telegram_id']


admin.site.register(ProductType)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')


admin.site.register(Purchase)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'type', 'user')
    search_fields = ['title', 'user', 'price', 'type']
