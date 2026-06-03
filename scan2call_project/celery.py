import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scan2call_project.settings")

app = Celery("scan2call_project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    "expire-chats": {
        "task": "apps.chat.tasks.expire_inactive_chats",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "subscription-expiry-reminder": {
        "task": "apps.subscriptions.tasks.send_expiry_reminders",
        "schedule": crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    "cleanup-old-notifications": {
        "task": "apps.notifications.tasks.cleanup_old_notifications",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
