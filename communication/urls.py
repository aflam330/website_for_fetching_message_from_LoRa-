"""
URL configuration for communication app
"""
from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    # Web views
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('node/<int:node_id>/', views.node_detail, name='node_detail'),
    
    # API endpoints for ESP32
    path('api/nodes/update-status/', views.api_update_status, name='api_update_status'),
    path('api/messages/send/', views.api_send_message, name='api_send_message'),
    path('api/messages/inbox/<str:esp32_device_id>/', views.api_get_inbox, name='api_get_inbox'),
]

