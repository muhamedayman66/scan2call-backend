from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.subscriptions.models import Plan, Subscription
from apps.vehicles.models import Vehicle

User = get_user_model()


class Command(BaseCommand):
    help = "Create test data for development"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating test data...")

        # Create test user
        user, created = User.objects.get_or_create(
            phone="+201234567890",
            defaults={
                "full_name": "Ahmed Mohamed",
                "email": "ahmed@example.com",
                "language": "ar",
                "is_verified": True,
            },
        )

        if created:
            user.set_password("password123")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {user.phone}"))

        # Create test vehicles
        vehicles_data = [
            {
                "brand": "toyota",
                "model": "Camry",
                "year": 2023,
                "color": "white",
                "plate": "ABC-1234",
            },
            {
                "brand": "bmw",
                "model": "X5",
                "year": 2022,
                "color": "black",
                "plate": "XYZ-5678",
            },
        ]

        for v_data in vehicles_data:
            vehicle, created = Vehicle.objects.get_or_create(
                plate_number=v_data["plate"],
                defaults={
                    "owner": user,
                    "brand": v_data["brand"],
                    "model": v_data["model"],
                    "year": v_data["year"],
                    "color": v_data["color"],
                    "show_phone": True,
                    "allow_call": True,
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created vehicle: {vehicle.plate_number}")
                )

        # Create active subscription
        plan = Plan.objects.filter(is_active=True).first()
        if plan:
            Subscription.objects.get_or_create(
                user=user,
                status="active",
                defaults={
                    "plan": plan,
                    "started_at": timezone.now(),
                    "expires_at": timezone.now() + timedelta(days=30),
                },
            )
            self.stdout.write(self.style.SUCCESS(f"Created subscription for user"))

        self.stdout.write(self.style.SUCCESS("Test data created successfully!"))
