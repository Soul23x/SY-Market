from django.contrib import admin
from .models import Store,StoreConfig


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'subdomain', 'owner', 'approval_status', 'is_active', 'is_featured', 'created_at']
    list_filter = ['approval_status', 'is_active', 'is_featured']
    search_fields = ['name', 'subdomain']

admin.site.register(StoreConfig)