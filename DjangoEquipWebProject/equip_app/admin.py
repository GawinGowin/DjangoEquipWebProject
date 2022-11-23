from django.contrib import admin
from .models import Equipmentmaincategory, Equipmentcategory, Equipment, Lending, Log

# Register your models here

class EquipmentmaincategoryAdmin(admin.ModelAdmin):
    fields = ['main_category',]
    list_display = ('main_category',)

admin.site.register(Equipmentmaincategory, EquipmentmaincategoryAdmin)

class EquipmentcategoryAdmin(admin.ModelAdmin):
    fields = ['category', 'main_category',]
    list_display = ('category', 'main_category',)
    
admin.site.register(Equipmentcategory, EquipmentcategoryAdmin)

class EquipmentAdmin(admin.ModelAdmin):
    fields = ['category', 'management_num', 'name', 'images', 'maker', 'feature', 'size', 'num',
              'URL','purchase_date','status', 'note',]
    list_display = ('name', 'category', 'maker', 'status','created','modified')

admin.site.register(Equipment, EquipmentAdmin)

class LogAdmin(admin.ModelAdmin):
    fields = ['item_name', 'times', 'available', 'now_user', 'previous_user', 'history',]
    list_display = ('item_name', 'times', 'available', 'now_user', 'previous_user')

admin.site.register(Log, LogAdmin)

class LendingAdmin(admin.ModelAdmin):
    fields = ['user', 'item_name', 'lend_date', 'lend_span', 'note']
    list_display = ('user', 'item_name', 'lend_date', 'lend_span', 'return_date')

admin.site.register(Lending,LendingAdmin)