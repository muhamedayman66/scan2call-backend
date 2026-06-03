import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Vehicle(models.Model):
    BRAND_CHOICES = [
        ("toyota", "Toyota"),
        ("bmw", "BMW"),
        ("mercedes", "Mercedes-Benz"),
        ("hyundai", "Hyundai"),
        ("kia", "Kia"),
        ("honda", "Honda"),
        ("nissan", "Nissan"),
        ("ford", "Ford"),
        ("chevrolet", "Chevrolet"),
        ("volkswagen", "Volkswagen"),
        ("peugeot", "Peugeot"),
        ("renault", "Renault"),
        ("fiat", "Fiat"),
        ("lada", "Lada"),
        ("mitsubishi", "Mitsubishi"),
        ("suzuki", "Suzuki"),
        ("mazda", "Mazda"),
        ("subaru", "Subaru"),
        ("jeep", "Jeep"),
        ("land_rover", "Land Rover"),
        ("range_rover", "Range Rover"),
        ("audi", "Audi"),
        ("porsche", "Porsche"),
        ("lexus", "Lexus"),
        ("infiniti", "Infiniti"),
        ("acura", "Acura"),
        ("volvo", "Volvo"),
        ("skoda", "Skoda"),
        ("seat", "SEAT"),
        ("opel", "Opel"),
        ("dacia", "Dacia"),
        ("chery", "Chery"),
        ("geely", "Geely"),
        ("byd", "BYD"),
        ("jac", "JAC"),
        ("mg", "MG"),
        ("haval", "Haval"),
        ("dongfeng", "Dongfeng"),
        ("jetour", "Jetour"),
        ("zotye", "Zotye"),
        ("gac", "GAC"),
        ("baic", "BAIC"),
        ("lifan", "Lifan"),
        ("changan", "Changan"),
        ("foton", "Foton"),
        ("great_wall", "Great Wall"),
        ("huanghai", "Huanghai"),
        ("king_long", "King Long"),
        ("yutong", "Yutong"),
        ("hino", "Hino"),
        ("tesla", "Tesla"),
        ("cadillac", "Cadillac"),
        ("dodge", "Dodge"),
        ("ram", "RAM"),
    ]

    COLOR_CHOICES = [
        ("white", "White"),
        ("black", "Black"),
        ("silver", "Silver"),
        ("gray", "Gray"),
        ("red", "Red"),
        ("blue", "Blue"),
        ("green", "Green"),
        ("yellow", "Yellow"),
        ("orange", "Orange"),
        ("brown", "Brown"),
        ("gold", "Gold"),
        ("beige", "Beige"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vehicles"
    )

    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    plate_number = models.CharField(max_length=20, unique=True, db_index=True)

    photo_1 = models.TextField(null=True, blank=True)
    photo_2 = models.TextField(null=True, blank=True)
    photo_3 = models.TextField(null=True, blank=True)

    # Settings
    show_phone = models.BooleanField(default=False)
    allow_call = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vehicles"
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "is_active"]),
            models.Index(fields=["plate_number"]),
        ]

    def __str__(self):
        return f"{self.get_brand_display()} {self.model} ({self.plate_number})"

    @property
    def photos(self):
        return [p for p in [self.photo_1, self.photo_2, self.photo_3] if p]
