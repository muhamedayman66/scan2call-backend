from django.apps import AppConfig


class VehiclesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.vehicles"
    verbose_name = "Vehicles"

    def ready(self):
        import apps.vehicles.signals  # noqa: F401
