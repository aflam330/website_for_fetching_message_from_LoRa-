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
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


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

