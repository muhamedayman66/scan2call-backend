from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Invoice, Plan, Subscription
from .serializers import (InvoiceSerializer, PlanSerializer,
                          SubscriptionSerializer)


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def current(self, request):
        """Get current active subscription"""
        subscription = Subscription.objects.filter(
            user=request.user, status="active", expires_at__gt=timezone.now()
        ).first()

        if subscription:
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)

        return Response(
            {"message": "No active subscription"}, status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=["post"])
    def subscribe(self, request):
        """Subscribe to a plan"""
        plan_id = request.data.get("plan_id")
        payment_method = request.data.get("payment_method", "card")

        if plan_id == "free":
            plan = Plan.objects.filter(price_egp=0).first()
            if not plan:
                plan = Plan.objects.create(
                    name="Standard Free Alpha",
                    name_ar="الباقة الأساسية",
                    description="Demo trial",
                    description_ar="للتجربة",
                    price_egp=0,
                    duration_days=30,
                    max_vehicles=1,
                    sticker_count=0,
                )
        else:
            try:
                plan = Plan.objects.get(id=plan_id, is_active=True)
            except Plan.DoesNotExist:
                return Response(
                    {"error": "Invalid plan"}, status=status.HTTP_400_BAD_REQUEST
                )

        # Cancel existing active subscriptions
        Subscription.objects.filter(user=request.user, status="active").update(
            status="cancelled", cancelled_at=timezone.now()
        )

        # Create new subscription
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            status="pending",
            payment_method=payment_method,
        )

        # Create invoice
        invoice = Invoice.objects.create(
            subscription=subscription,
            amount=plan.price_egp,
            invoice_number=f"INV-{subscription.id.hex[:8].upper()}",
        )

        # TODO: Integrate actual payment gateway (Paymob, Fawry, etc.)
        # For now, auto-approve
        subscription.status = "active"
        subscription.started_at = timezone.now()
        subscription.expires_at = timezone.now() + timedelta(days=plan.duration_days)
        subscription.save()

        invoice.payment_status = "paid"
        invoice.paid_at = timezone.now()
        invoice.save()

        return Response(
            {
                "subscription": SubscriptionSerializer(subscription).data,
                "invoice": InvoiceSerializer(invoice).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel subscription"""
        subscription = self.get_object()

        if subscription.status != "active":
            return Response(
                {"error": "Subscription is not active"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.status = "cancelled"
        subscription.cancelled_at = timezone.now()
        subscription.auto_renew = False
        subscription.save()

        return Response(SubscriptionSerializer(subscription).data)


class InvoiceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return (
            Invoice.objects.filter(subscription__user=self.request.user)
            .select_related("subscription__plan")
            .order_by("-created_at")
        )


class InstapayPaymentRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    from .serializers import InstapayPaymentRequestSerializer

    serializer_class = InstapayPaymentRequestSerializer

    def get_queryset(self):
        from .models import InstapayPaymentRequest

        if self.request.user.is_staff:
            return InstapayPaymentRequest.objects.all()
        return InstapayPaymentRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        import uuid

        pay_id = f"pay-{uuid.uuid4().hex[:8]}"
        serializer.save(user=self.request.user, id=pay_id)
