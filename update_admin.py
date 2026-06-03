import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scan2call_project.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    admin_user = User.objects.get(phone="0000000000")
    admin_user.delete()
except User.DoesNotExist:
    pass

try:
    if not User.objects.filter(phone="scan2call").exists():
        admin_user = User.objects.create_superuser(
            phone="scan2call",
            password="admin123",
            full_name="System Admin"
        )
        print("SUCCESS: Admin 'scan2call' created.")
    else:
        admin_user = User.objects.get(phone="scan2call")
        admin_user.set_password("admin123")
        admin_user.save()
        print("SUCCESS: Admin 'scan2call' password updated.")
except Exception as e:
    print(f"ERROR: {e}")
