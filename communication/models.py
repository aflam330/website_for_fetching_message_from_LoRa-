"""
Models for communication app - Messages
"""
from django.db import models
from accounts.models import Node


class Message(models.Model):
    """
    Represents a message sent from one node to another.
    """
    STATUS_CHOICES = [
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
    ]

    MESSAGE_TYPE_CHOICES = [
        ('TEXT', 'Text'),
    ]

    sender = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="The node that sent this message"
    )
    receiver = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='received_messages',
        help_text="The node that should receive this message"
    )
    content = models.TextField(
        help_text="The message content/payload"
    )
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default='TEXT',
        help_text="Type of message"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='SENT',
        help_text="Delivery status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['receiver', '-created_at']),
        ]

    def __str__(self):
        return f"Message from {self.sender.node_name} to {self.receiver.node_name} ({self.created_at})"

