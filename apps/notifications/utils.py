import logging
import os

import firebase_admin
from django.conf import settings
from firebase_admin import credentials, messaging
from twilio.rest import Client

logger = logging.getLogger(__name__)

# Initialize Firebase — بيشتغل بس لو الـ credentials file موجود
FIREBASE_AVAILABLE = False

try:
    if not firebase_admin._apps:
        cred_path = str(settings.FIREBASE_CREDENTIALS_PATH)
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            FIREBASE_AVAILABLE = True
        else:
            logger.warning(
                "Firebase credentials file not found — push notifications disabled."
            )
    else:
        FIREBASE_AVAILABLE = True
except Exception as e:
    logger.error(f"Firebase initialization error: {e}")


def send_fcm_notification(user, title, message, data=None, priority="normal"):
    """Send FCM push notification to user and log it in the database"""

    # ALWAYS create the notification log first so it appears in the app
    from .models import NotificationLog

    notification_log = NotificationLog.objects.create(
        user=user,
        type=data.get("type", "system") if data else "system",
        priority=priority,
        title=title,
        message=message,
        data=data or {},
        is_sent=False,
    )

    if not FIREBASE_AVAILABLE:
        logger.warning(
            "Firebase not available — skipping push notification, but logged to DB."
        )
        return None

    if not user.fcm_token:
        logger.warning(f"No FCM token for user {user.id}")
        return None

    try:
        notification = messaging.Notification(title=title, body=message)

        android_priority = "high" if priority in ["high", "critical"] else "normal"
        android_config = messaging.AndroidConfig(
            priority=android_priority,
            notification=messaging.AndroidNotification(
                sound="default", channel_id="scan2call_notifications"
            ),
        )

        apns_config = messaging.APNSConfig(
            payload=messaging.APNSPayload(aps=messaging.Aps(sound="default", badge=1))
        )

        fcm_message = messaging.Message(
            notification=notification,
            data=data or {},
            token=user.fcm_token,
            android=android_config,
            apns=apns_config,
        )

        response = messaging.send(fcm_message)
        logger.info(f"FCM sent to {user.id}: {response}")

        # Update log to indicate FCM was sent
        notification_log.is_sent = True
        notification_log.fcm_message_id = response
        notification_log.save(update_fields=["is_sent", "fcm_message_id"])

        return response

    except Exception as e:
        logger.error(f"FCM error: {e}")
        return None


def send_sms(phone, message):
    """Send SMS via Twilio"""
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        sms = client.messages.create(
            body=message, from_=settings.TWILIO_PHONE_NUMBER, to=phone
        )
        logger.info(f"SMS sent to {phone}: {sms.sid}")
        return sms.sid

    except Exception as e:
        logger.error(f"SMS error: {e}")
        return None
