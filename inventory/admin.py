from django.contrib import admin

# Register your models here.
from inventory.models import Item, Category
from import_export.admin import ExportMixin
class ItemAdmin(ExportMixin, admin.ModelAdmin): pass
admin.site.register(Item, ItemAdmin)
admin.site.register(Category) 