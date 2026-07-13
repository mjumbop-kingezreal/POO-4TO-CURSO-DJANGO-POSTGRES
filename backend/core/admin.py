from django.contrib import admin
from .models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_link', 'order', 'url_name', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'url_name']
    ordering = ['order', 'name']
    filter_horizontal = ['permissions']
    list_editable = ['order', 'is_active']

    def parent_link(self, obj):
        return obj.parent.name if obj.parent else '—'
    parent_link.short_description = 'Módulo padre'
    parent_link.admin_order_field = 'parent'

    def get_queryset(self, request):
        return MenuItem.all_objects.all()