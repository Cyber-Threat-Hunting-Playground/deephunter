from django.contrib import admin
from .models import AppSetting, Module, ModulePermission

class ModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('module__name', 'action', 'description', 'permission')
    list_filter = ['module__name', 'permission']
    search_fields = ['action', 'description', 'permission']

admin.site.register(Module)
admin.site.register(ModulePermission, ModulePermissionAdmin)
admin.site.register(AppSetting)
