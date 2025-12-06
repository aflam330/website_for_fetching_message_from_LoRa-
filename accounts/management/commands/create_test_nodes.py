"""
Django management command to create test nodes for development.
Usage: python manage.py create_test_nodes
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Node


class Command(BaseCommand):
    help = 'Creates 5 test nodes (Node1 through Node5) for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating test nodes...')

        # Create 5 test nodes
        for i in range(1, 6):
            username = f'node{i}'
            node_name = f'Node {i}'
            esp32_device_id = f'ESP32-00{i}'
            lora_node_id = f'LORA-00{i}'
            password = 'testpass123'  # Simple password for testing

            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'User {username} already exists. Skipping...'))
                continue

            # Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=f'node{i}@example.com'
            )

            # Create node profile
            node = Node.objects.create(
                user=user,
                node_name=node_name,
                esp32_device_id=esp32_device_id,
                lora_node_id=lora_node_id,
                status='OFFLINE',
                description=f'Test node {i} for LoRa communication system'
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {node_name}:\n'
                    f'  Username: {username}\n'
                    f'  Password: {password}\n'
                    f'  ESP32 ID: {esp32_device_id}\n'
                    f'  LoRa ID: {lora_node_id}\n'
                )
            )

        self.stdout.write(self.style.SUCCESS('\nSuccessfully created test nodes!'))
        self.stdout.write('\nYou can now login with any of these accounts:')
        self.stdout.write('  node1 / testpass123')
        self.stdout.write('  node2 / testpass123')
        self.stdout.write('  node3 / testpass123')
        self.stdout.write('  node4 / testpass123')
        self.stdout.write('  node5 / testpass123')

