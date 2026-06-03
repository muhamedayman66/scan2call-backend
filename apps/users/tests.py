from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class UserAuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/auth/register/"
        self.login_url = "/api/auth/login/"

        self.user_data = {
            "phone": "+201234567890",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
            "language": "en",
        }

    def test_user_registration(self):
        """Test user can register successfully"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn("user", response.data)

    def test_user_login(self):
        """Test user can login successfully"""
        # First register
        User.objects.create_user(
            phone=self.user_data["phone"],
            full_name=self.user_data["full_name"],
            password=self.user_data["password"],
        )

        # Then login
        response = self.client.post(
            self.login_url,
            {"phone": self.user_data["phone"], "password": self.user_data["password"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_duplicate_phone_registration(self):
        """Test cannot register with duplicate phone"""
        User.objects.create_user(
            phone=self.user_data["phone"],
            full_name=self.user_data["full_name"],
            password=self.user_data["password"],
        )

        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
