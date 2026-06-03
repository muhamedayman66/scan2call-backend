from django.shortcuts import get_object_or_404, render

from .models import QRCode


def qr_page_view(request, qr_hash):
    """Guest QR code landing page"""
    qr = get_object_or_404(QRCode, code_hash=qr_hash, is_active=True)
    qr.increment_scan()

    vehicle = qr.vehicle
    owner = vehicle.owner

    if owner.subscription_status != "ACTIVE":
        return render(
            request,
            "guest/qr_inactive.html",
            {"language": request.GET.get("lang", "en")},
        )

    language = request.GET.get("lang", "en")

    context = {
        "qr_hash": qr_hash,
        "vehicle": vehicle,
        "owner_name": owner.first_name,
        "owner_photo": owner.profile_photo if owner.profile_photo else None,
        "show_phone": owner.show_phone_in_requests,
        "allow_call": vehicle.allow_call,
        "owner_phone": owner.phone if owner.show_phone_in_requests else None,
        "language": language,
    }

    return render(request, "guest/qr_page.html", context)
