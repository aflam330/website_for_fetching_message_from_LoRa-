"""
Models for accounts app - Node/User profiles
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Node(models.Model):
    """
    Represents a physical ESP32 + LoRa node.
    Each node is linked to a User account.
    """
    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='node_profile',
        help_text="The Django user account linked to this node"
    )
    node_name = models.CharField(
        max_length=100,
        help_text="Human-readable name for this node (e.g., 'Node A', 'Hilltop Node')"
    )
    esp32_device_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique hardware identifier for the ESP32 device"
    )
    lora_node_id = models.CharField(
        max_length=50,
        help_text="LoRa network address or node ID"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='OFFLINE',
        help_text="Current connection status"
    )
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this node updated its status"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description or location information"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['node_name']

    def __str__(self):
        return f"{self.node_name} ({self.esp32_device_id})"

    def clean(self):
        """Validate that esp32_device_id is unique"""
        if Node.objects.filter(esp32_device_id=self.esp32_device_id).exclude(pk=self.pk).exists():
            raise ValidationError({'esp32_device_id': 'This ESP32 device ID is already registered.'})


