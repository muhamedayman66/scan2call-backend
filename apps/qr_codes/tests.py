from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.vehicles.models import Vehicle

from .models import QRCode

User = get_user_model()


class QRCodeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="+201234567890", full_name="Test User", password="testpass123"
        )

        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            brand="toyota",
            model="Camry",
            year=2023,
            color="white",
            plate_number="ABC-1234",
        )

    def test_qr_code_auto_creation(self):
        """Test QR code is auto-created with vehicle"""
        self.assertTrue(hasattr(self.vehicle, "qr_code"))
        self.assertIsNotNone(self.vehicle.qr_code.code_hash)

    def test_qr_code_uniqueness(self):
        """Test QR code hash is unique"""
        vehicle2 = Vehicle.objects.create(
            owner=self.user,
            brand="bmw",
            model="X5",
            year=2022,
            color="black",
            plate_number="XYZ-5678",
        )

        self.assertNotEqual(self.vehicle.qr_code.code_hash, vehicle2.qr_code.code_hash)

    def test_scan_count_increment(self):
        """Test scan count increments correctly"""
        qr_code = self.vehicle.qr_code
        initial_count = qr_code.scan_count

        qr_code.increment_scan()
        qr_code.refresh_from_db()

        self.assertEqual(qr_code.scan_count, initial_count + 1)
