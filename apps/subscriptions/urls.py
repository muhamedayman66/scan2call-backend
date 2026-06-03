from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"plans", views.PlanViewSet, basename="plan")
router.register(r"subscriptions", views.SubscriptionViewSet, basename="subscription")
router.register(r"instapay", views.InstapayPaymentRequestViewSet, basename="instapay")

urlpatterns = [
    path("billing/invoices/", views.InvoiceListView.as_view(), name="invoice-list"),
    path("", include(router.urls)),
]
