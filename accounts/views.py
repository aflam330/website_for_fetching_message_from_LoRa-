"""
Views for accounts app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from .forms import NodeRegistrationForm
from .models import Node
from communication.models import Message


def home(request):
    """
    Home page showing overall statistics and links.
    """
    total_nodes = Node.objects.count()
    online_nodes = Node.objects.filter(status='ONLINE').count()
    offline_nodes = Node.objects.filter(status='OFFLINE').count()

    context = {
        'total_nodes': total_nodes,
        'online_nodes': online_nodes,
        'offline_nodes': offline_nodes,
    }
    return render(request, 'home.html', context)


def register(request):
    """
    Registration view for new nodes/users.
    """
    if request.method == 'POST':
        form = NodeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Node "{form.cleaned_data["node_name"]}" registered successfully! Please log in.')
            return redirect('accounts:login')
    else:
        form = NodeRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    """
    Custom login view with Tailwind styling context.
    Validates that the user type matches the selected login type.
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """
        Override form_valid to check if user type matches selected login type.
        """
        login_type = self.request.POST.get('login_type', 'node')
        user = form.get_user()
        
        # Check if user type matches selected login type
        is_admin = user.is_staff or user.is_superuser
        
        if login_type == 'node' and is_admin:
            # Admin trying to log in as node user
            form.add_error(None, 'You selected "Node User" but this account is an admin. Please select "Admin" to log in.')
            return self.form_invalid(form)
        elif login_type == 'admin' and not is_admin:
            # Node user trying to log in as admin
            form.add_error(None, 'You selected "Admin" but this account is not an admin. Please select "Node User" to log in.')
            return self.form_invalid(form)
        
        # User type matches, proceed with normal login
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Redirect users to the appropriate dashboard based on their user type.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            from django.urls import reverse
            return reverse('communication:admin_dashboard')
        else:
            return super().get_success_url()


@login_required
def node_dashboard(request):
    """
    Dashboard for logged-in node users.
    Shows node info, connection status, send message form, inbox, and outbox.
    """
    # Prevent admin/staff users from accessing node dashboard
    if request.user.is_staff or request.user.is_superuser:
        messages.info(request, 'Admin users should use the Admin Dashboard instead.')
        return redirect('communication:admin_dashboard')
    
    try:
        node = request.user.node_profile
    except Node.DoesNotExist:
        messages.error(request, 'No node profile found for your account. Please contact an administrator.')
        return redirect('accounts:home')

    # Handle message sending
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        content = request.POST.get('content', '').strip()

        if not receiver_id or not content:
            messages.error(request, 'Please select a receiver and enter a message.')
        else:
            try:
                receiver = get_object_or_404(Node, pk=receiver_id)
                if receiver.pk == node.pk:
                    messages.error(request, 'You cannot send a message to yourself.')
                else:
                    Message.objects.create(
                        sender=node,
                        receiver=receiver,
                        content=content,
                        status='SENT'
                    )
                    messages.success(request, f'Message sent to {receiver.node_name} successfully!')
                    return redirect('accounts:node_dashboard')
            except Exception as e:
                messages.error(request, f'Error sending message: {str(e)}')

    # Get other nodes for the message form dropdown
    other_nodes = Node.objects.exclude(pk=node.pk).order_by('node_name')

    # Get inbox (messages received by this node)
    inbox_messages = node.received_messages.all()[:50]  # Last 50 messages

    # Get outbox (messages sent by this node)
    outbox_messages = node.sent_messages.all()[:50]  # Last 50 messages

    context = {
        'node': node,
        'other_nodes': other_nodes,
        'inbox_messages': inbox_messages,
        'outbox_messages': outbox_messages,
    }
    return render(request, 'accounts/node_dashboard.html', context)

