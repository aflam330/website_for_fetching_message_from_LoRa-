"""
Admin configuration for communication app
"""
from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'content_preview', 'status', 'created_at']
    list_filter = ['status', 'message_type', 'created_at']
    search_fields = ['content', 'sender__node_name', 'receiver__node_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        """Show first 50 characters of message content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

