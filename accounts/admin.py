"""
Admin configuration for accounts app
"""
from django.contrib import admin
from .models import Node


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ['node_name', 'esp32_device_id', 'lora_node_id', 'status', 'last_seen', 'user']
    list_filter = ['status', 'created_at']
    search_fields = ['node_name', 'esp32_device_id', 'lora_node_id']
    readonly_fields = ['created_at', 'updated_at']

