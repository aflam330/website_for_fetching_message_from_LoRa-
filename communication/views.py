"""
Views for communication app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from .models import Message
from accounts.models import Node


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_dashboard(request):
    """
    Admin dashboard showing all nodes and messages.
    Only accessible to staff/superuser.
    """
    total_nodes = Node.objects.count()
    online_nodes = Node.objects.filter(status='ONLINE').count()
    offline_nodes = Node.objects.filter(status='OFFLINE').count()

    # Get all nodes
    all_nodes = Node.objects.all().order_by('node_name')

    # Get recent messages (last 50)
    recent_messages = Message.objects.all()[:50]

    context = {
        'total_nodes': total_nodes,
        'online_nodes': online_nodes,
        'offline_nodes': offline_nodes,
        'all_nodes': all_nodes,
        'recent_messages': recent_messages,
    }
    return render(request, 'communication/admin_dashboard.html', context)


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def node_detail(request, node_id):
    """
    Admin view to see details of a specific node.
    """
    node = get_object_or_404(Node, pk=node_id)
    
    # Get messages for this node
    sent_messages = node.sent_messages.all()[:50]
    received_messages = node.received_messages.all()[:50]

    context = {
        'node': node,
        'sent_messages': sent_messages,
        'received_messages': received_messages,
    }
    return render(request, 'communication/node_detail.html', context)


# ==================== API ENDPOINTS FOR ESP32 ====================

@csrf_exempt
@require_http_methods(["POST"])
def api_update_status(request):
    """
    API endpoint for ESP32 to update node status.
    POST /api/nodes/update-status/
    Request: {"esp32_device_id": "ESP32-001", "status": "ONLINE"}
    """
    try:
        data = json.loads(request.body)
        esp32_device_id = data.get('esp32_device_id')
        status = data.get('status', 'ONLINE').upper()

        if not esp32_device_id:
            return JsonResponse({'error': 'esp32_device_id is required'}, status=400)

        if status not in ['ONLINE', 'OFFLINE']:
            return JsonResponse({'error': 'status must be ONLINE or OFFLINE'}, status=400)

        try:
            node = Node.objects.get(esp32_device_id=esp32_device_id)
            node.status = status
            node.last_seen = timezone.now()
            node.save()
            return JsonResponse({
                'success': True,
                'message': f'Status updated to {status}',
                'node_name': node.node_name
            })
        except Node.DoesNotExist:
            return JsonResponse({'error': 'Node not found'}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_send_message(request):
    """
    API endpoint for ESP32 to send messages.
    POST /api/messages/send/
    Request: {
        "from_esp32_device_id": "ESP32-001",
        "to_esp32_device_id": "ESP32-002",
        "payload": "Hello from Node 1"
    }
    """
    try:
        data = json.loads(request.body)
        from_esp32_id = data.get('from_esp32_device_id')
        to_esp32_id = data.get('to_esp32_device_id')
        payload = data.get('payload', '')

        if not all([from_esp32_id, to_esp32_id, payload]):
            return JsonResponse({
                'error': 'from_esp32_device_id, to_esp32_device_id, and payload are required'
            }, status=400)

        try:
            sender_node = Node.objects.get(esp32_device_id=from_esp32_id)
            receiver_node = Node.objects.get(esp32_device_id=to_esp32_id)

            message = Message.objects.create(
                sender=sender_node,
                receiver=receiver_node,
                content=payload,
                status='SENT'
            )

            return JsonResponse({
                'success': True,
                'message_id': message.id,
                'message': 'Message sent successfully'
            })
        except Node.DoesNotExist as e:
            return JsonResponse({'error': f'Node not found: {str(e)}'}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_get_inbox(request, esp32_device_id):
    """
    API endpoint for ESP32 to fetch messages.
    GET /api/messages/inbox/<esp32_device_id>/
    Returns JSON list of messages for that node.
    """
    try:
        node = Node.objects.get(esp32_device_id=esp32_device_id)
        messages = node.received_messages.all()[:50]  # Last 50 messages

        messages_data = [{
            'id': msg.id,
            'from': {
                'node_name': msg.sender.node_name,
                'esp32_device_id': msg.sender.esp32_device_id,
            },
            'content': msg.content,
            'status': msg.status,
            'created_at': msg.created_at.isoformat(),
        } for msg in messages]

        return JsonResponse({
            'success': True,
            'node_name': node.node_name,
            'messages': messages_data,
            'count': len(messages_data)
        })

    except Node.DoesNotExist:
        return JsonResponse({'error': 'Node not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

