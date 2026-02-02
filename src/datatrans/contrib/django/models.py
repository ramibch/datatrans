from django.conf import settings
from django.db import models
from django.utils import timezone


class DatatransTransaction(models.Model):
    """Store Datatrans transaction information."""

    STATUS_CHOICES = [
        ("initialized", "Initialized"),
        ("authorized", "Authorized"),
        ("settled", "Settled"),
        ("canceled", "Canceled"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    transaction_id = models.CharField(max_length=50, unique=True)
    merchant_reference = models.CharField(max_length=40, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    payment_method = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="initialized"
    )

    # Card/alias information
    masked_card = models.CharField(max_length=50, null=True, blank=True)
    alias = models.CharField(max_length=100, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    authorized_at = models.DateTimeField(null=True, blank=True)
    settled_at = models.DateTimeField(null=True, blank=True)

    # Additional data
    raw_request = models.JSONField(null=True, blank=True)
    raw_response = models.JSONField(null=True, blank=True)
    webhook_data = models.JSONField(null=True, blank=True)

    # Foreign key to your order/user model
    order = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Adjust to your order model
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="datatrans_transactions",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["merchant_reference"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.merchant_reference} ({self.status})"

    def update_status(self, new_status: str, data: dict | None = None):
        """Update transaction status with timestamp."""
        self.status = new_status
        self.updated_at = timezone.now()

        if new_status == "authorized":
            self.authorized_at = timezone.now()
        elif new_status == "settled":
            self.settled_at = timezone.now()

        if data:
            self.webhook_data = data

        self.save()
