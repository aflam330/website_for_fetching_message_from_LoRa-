"""
Forms for communication app
"""
from django import forms
from .models import Message
from accounts.models import Node


class MessageForm(forms.ModelForm):
    """
    Form for sending messages between nodes.
    """
    receiver = forms.ModelChoiceField(
        queryset=Node.objects.none(),  # Will be set in view
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
        }),
        help_text="Select the target node"
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'rows': 5,
            'placeholder': 'Enter your message here...'
        }),
        help_text="Message content"
    )

    class Meta:
        model = Message
        fields = ['receiver', 'content']

