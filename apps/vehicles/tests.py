from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Vehicle

User = get_user_model()


class VehicleTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone="+201234567890", full_name="Test User", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.vehicle_data = {
            "brand": "toyota",
            "model": "Camry",
            "year": 2023,
            "color": "white",
            "plate_number": "ABC-1234",
            "show_phone": True,
            "allow_call": True,
        }

    def test_create_vehicle(self):
        """Test vehicle creation"""
        response = self.client.post("/api/vehicles/", self.vehicle_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vehicle.objects.count(), 1)

        # Check QR code was created
        vehicle = Vehicle.objects.first()
        self.assertTrue(hasattr(vehicle, "qr_code"))

    def test_list_vehicles(self):
        """Test listing user vehicles"""
        Vehicle.objects.create(owner=self.user, **self.vehicle_data)

        response = self.client.get("/api/vehicles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_duplicate_plate_number(self):
        """Test cannot create vehicle with duplicate plate"""
        Vehicle.objects.create(owner=self.user, **self.vehicle_data)

        response = self.client.post("/api/vehicles/", self.vehicle_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
