# LoRa ESP32 Communication Dashboard

A Django web application for managing and monitoring LoRa communication between ESP32 nodes.

## Features

- **Node Management**: Register and track ESP32 + LoRa nodes
- **Status Tracking**: Monitor which nodes are online/offline
- **Message System**: Send and receive messages between nodes
- **User Dashboards**: 
  - Individual node dashboards for each user
  - Admin dashboard for system-wide overview
- **REST API**: Endpoints for ESP32 devices to update status and send/receive messages

## Tech Stack

- **Python 3.x** (latest stable)
- **Django 5.0+** (latest stable)
- **Tailwind CSS** (via CDN)
- **SQLite** (default database)

## Project Structure

```
lora_comm/
├── lora_comm/          # Main project settings
├── accounts/           # User/Node management app
│   ├── models.py       # Node model
│   ├── views.py        # Auth and node dashboard views
│   ├── forms.py        # Registration form
│   └── management/     # Management commands
├── communication/      # Messages and admin dashboard app
│   ├── models.py       # Message model
│   ├── views.py        # Admin dashboard and API views
│   └── forms.py        # Message form
└── templates/          # HTML templates with Tailwind CSS
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install Django
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate
```

### 3. Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account. This account will have access to the admin dashboard.

### 4. Create Test Nodes (Optional)

To quickly create 5 test nodes for development:

```bash
python manage.py create_test_nodes
```

This creates:
- **node1** through **node5** (username)
- Password: **testpass123** (for all)
- ESP32 IDs: ESP32-001 through ESP32-005
- LoRa IDs: LORA-001 through LORA-005

### 5. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

## Accessing the Application

### Home Page
- **URL**: http://127.0.0.1:8000/
- Shows overall statistics (total nodes, online/offline counts)
- Links to login, register, and admin dashboard

### User Registration
- **URL**: http://127.0.0.1:8000/register/
- Register a new ESP32 + LoRa node
- Requires: username, password, node name, ESP32 device ID, LoRa node ID

### Login
- **URL**: http://127.0.0.1:8000/login/
- Login with your node account credentials

### Node Dashboard
- **URL**: http://127.0.0.1:8000/dashboard/
- **Access**: Requires login
- Features:
  - View node status and information
  - Send messages to other nodes
  - View inbox (received messages)
  - View outbox (sent messages)

### Admin Dashboard
- **URL**: http://127.0.0.1:8000/communication/admin-dashboard/
- **Access**: Requires staff/superuser privileges
- Features:
  - View all nodes and their status
  - View all messages
  - View detailed information for each node

### Django Admin
- **URL**: http://127.0.0.1:8000/admin/
- **Access**: Requires superuser account
- Full Django admin interface for managing nodes and messages

## API Endpoints for ESP32

The application provides REST-like endpoints that ESP32 devices can call over HTTP/WiFi.

### 1. Update Node Status

**Endpoint**: `POST /communication/api/nodes/update-status/`

**Request Body** (JSON):
```json
{
    "esp32_device_id": "ESP32-001",
    "status": "ONLINE"
}
```

**Response** (Success):
```json
{
    "success": true,
    "message": "Status updated to ONLINE",
    "node_name": "Node 1"
}
```

**cURL Example**:
```bash
curl -X POST http://127.0.0.1:8000/communication/api/nodes/update-status/ \
  -H "Content-Type: application/json" \
  -d '{"esp32_device_id": "ESP32-001", "status": "ONLINE"}'
```

### 2. Send Message

**Endpoint**: `POST /communication/api/messages/send/`

**Request Body** (JSON):
```json
{
    "from_esp32_device_id": "ESP32-001",
    "to_esp32_device_id": "ESP32-002",
    "payload": "Hello from Node 1!"
}
```

**Response** (Success):
```json
{
    "success": true,
    "message_id": 1,
    "message": "Message sent successfully"
}
```

**cURL Example**:
```bash
curl -X POST http://127.0.0.1:8000/communication/api/messages/send/ \
  -H "Content-Type: application/json" \
  -d '{"from_esp32_device_id": "ESP32-001", "to_esp32_device_id": "ESP32-002", "payload": "Hello!"}'
```

### 3. Get Inbox Messages

**Endpoint**: `GET /communication/api/messages/inbox/<esp32_device_id>/`

**Response** (Success):
```json
{
    "success": true,
    "node_name": "Node 1",
    "messages": [
        {
            "id": 1,
            "from": {
                "node_name": "Node 2",
                "esp32_device_id": "ESP32-002"
            },
            "content": "Hello from Node 2!",
            "status": "SENT",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ],
    "count": 1
}
```

**cURL Example**:
```bash
curl http://127.0.0.1:8000/communication/api/messages/inbox/ESP32-001/
```

## User Types

### Admin Users
- Created via `python manage.py createsuperuser`
- Can access admin dashboard
- Can view all nodes and messages
- Can view individual node details

### Node Users
- Created via registration page or management command
- Each user represents one ESP32 + LoRa node
- Can access their own dashboard
- Can send messages to other nodes
- Can view their inbox and outbox

## Models

### Node Model
- `user`: OneToOne link to Django User
- `node_name`: Human-readable name
- `esp32_device_id`: Unique hardware identifier
- `lora_node_id`: LoRa network address
- `status`: ONLINE or OFFLINE
- `last_seen`: Last status update timestamp
- `description`: Optional description/location

### Message Model
- `sender`: ForeignKey to Node
- `receiver`: ForeignKey to Node
- `content`: Message text
- `message_type`: Currently only TEXT
- `status`: SENT or DELIVERED
- `created_at`: Timestamp

## Development Notes

- The project uses SQLite by default (good for development)
- Tailwind CSS is loaded via CDN (no build step required)
- All API endpoints are CSRF-exempt for ESP32 compatibility
- Node status updates automatically set `last_seen` timestamp

## Future Enhancements

Possible extensions:
- Message delivery confirmation
- Message routing through multiple nodes
- Real-time updates using WebSockets
- Message encryption
- Node location tracking
- Message history and search
- Custom message types (sensor data, commands, etc.)

## License

This project is provided as-is for educational and development purposes.

Install dependencies:
   pip install -r requirements.txt
Run migrations:
   python manage.py makemigrations   python manage.py migrate
Create admin user:
   python manage.py createsuperuser
(Optional) Create test nodes:
   python manage.py create_test_nodes
Start the server:
   python manage.py runserver
Access the app:
Home: http://127.0.0.1:8000/
Login: http://127.0.0.1:8000/login/
Register: http://127.0.0.1:8000/register/
Admin Dashboard: http://127.0.0.1:8000/communication/admin-dashboard/
Login page: http://127.0.0.1:8000/login/
Admin Dashboard: http://127.0.0.1:8000/communication/admin-dashboard/
Django Admin: http://127.0.0.1:8000/admin/
