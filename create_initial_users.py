import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scan2call_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()

# Create Admin User
admin_phone = "0000000000"
if not User.objects.filter(phone=admin_phone).exists():
    admin_user = User.objects.create_superuser(
        phone=admin_phone,
        password="adminpassword123",
        full_name="System Admin"
    )
    print("Admin user created successfully. Phone:", admin_phone, "Password: adminpassword123")
else:
    print("Admin user already exists.")

# Create Customer Service User
cs_phone = "1111111111"
if not User.objects.filter(phone=cs_phone).exists():
    cs_user = User.objects.create_user(
        phone=cs_phone,
        password="cspassword123",
        full_name="Customer Service Team"
    )
    cs_user.is_staff = True
    cs_user.save()
    
    # We can create a group for customer service with fewer permissions if needed
    cs_group, created = Group.objects.get_or_create(name="Customer Service")
    cs_user.groups.add(cs_group)

    print("Customer Service user created successfully. Phone:", cs_phone, "Password: cspassword123")
else:
    print("Customer Service user already exists.")
