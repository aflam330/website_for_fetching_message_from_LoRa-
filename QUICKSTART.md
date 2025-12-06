# Quick Start Guide

## Initial Setup (First Time)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create admin user:**
   ```bash
   python manage.py createsuperuser
   ```
   Follow prompts to create an admin account.

4. **Create test nodes (optional):**
   ```bash
   python manage.py create_test_nodes
   ```
   This creates 5 test nodes:
   - Usernames: `node1`, `node2`, `node3`, `node4`, `node5`
   - Password: `testpass123` (for all)
   - ESP32 IDs: `ESP32-001` through `ESP32-005`

5. **Start the server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the application:**
   - Home: http://127.0.0.1:8000/
   - Admin Dashboard: http://127.0.0.1:8000/communication/admin-dashboard/
   - Django Admin: http://127.0.0.1:8000/admin/

## Daily Usage

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```

2. **Login:**
   - Go to http://127.0.0.1:8000/login/
   - Use your node credentials or admin credentials

3. **For Node Users:**
   - Access dashboard at http://127.0.0.1:8000/dashboard/
   - Send messages, view inbox/outbox

4. **For Admin Users:**
   - Access admin dashboard at http://127.0.0.1:8000/communication/admin-dashboard/
   - View all nodes and messages

## Testing API Endpoints

### Update Node Status
```bash
curl -X POST http://127.0.0.1:8000/communication/api/nodes/update-status/ \
  -H "Content-Type: application/json" \
  -d "{\"esp32_device_id\": \"ESP32-001\", \"status\": \"ONLINE\"}"
```

### Send Message
```bash
curl -X POST http://127.0.0.1:8000/communication/api/messages/send/ \
  -H "Content-Type: application/json" \
  -d "{\"from_esp32_device_id\": \"ESP32-001\", \"to_esp32_device_id\": \"ESP32-002\", \"payload\": \"Hello!\"}"
```

### Get Inbox
```bash
curl http://127.0.0.1:8000/communication/api/messages/inbox/ESP32-001/
```

## Common Commands

- **Create migrations:** `python manage.py makemigrations`
- **Apply migrations:** `python manage.py migrate`
- **Create superuser:** `python manage.py createsuperuser`
- **Create test nodes:** `python manage.py create_test_nodes`
- **Run server:** `python manage.py runserver`
- **Access Django shell:** `python manage.py shell`

