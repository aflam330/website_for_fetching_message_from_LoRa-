"""
Forms for accounts app
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Node


class NodeRegistrationForm(UserCreationForm):
    """
    Registration form for new nodes/users.
    Extends Django's UserCreationForm with node-specific fields.
    """
    node_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'e.g., Node A'
        }),
        help_text="A human-readable name for this node"
    )
    esp32_device_id = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'ESP32-001'
        }),
        help_text="Unique hardware identifier for your ESP32 device"
    )
    lora_node_id = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'LORA-001'
        }),
        help_text="LoRa network address or node ID"
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'rows': 3,
            'placeholder': 'Optional description or location'
        })
    )
    contact_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'your.email@example.com'
        }),
        help_text="Contact email address"
    )
    contact_phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': '+8801234567890'
        }),
        help_text="Contact phone number"
    )
    contact_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Please enter your name'
        }),
        help_text="Name of the person responsible for this node"
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'node_name', 'esp32_device_id', 'lora_node_id', 'description', 'contact_email', 'contact_phone', 'contact_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind classes to default fields
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Confirm password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Create Node profile for this user
            Node.objects.create(
                user=user,
                node_name=self.cleaned_data['node_name'],
                esp32_device_id=self.cleaned_data['esp32_device_id'],
                lora_node_id=self.cleaned_data['lora_node_id'],
                description=self.cleaned_data.get('description', ''),
                contact_email=self.cleaned_data.get('contact_email', ''),
                contact_phone=self.cleaned_data.get('contact_phone', ''),
                contact_name=self.cleaned_data.get('contact_name', '')
            )
        return user

    def clean_esp32_device_id(self):
        esp32_device_id = self.cleaned_data.get('esp32_device_id')
        if Node.objects.filter(esp32_device_id=esp32_device_id).exists():
            raise forms.ValidationError("This ESP32 device ID is already registered.")
        return esp32_device_id

