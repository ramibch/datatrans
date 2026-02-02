import hashlib
import hmac
import time

from .exceptions import WebhookVerificationError


class WebhookVerifier:
    """Verify Datatrans webhook signatures."""

    def __init__(self, hmac_key: str):
        """
        Initialize with HMAC key from Datatrans dashboard.

        Args:
            hmac_key: Hex-encoded HMAC key from dashboard
        """
        self.hmac_key = bytes.fromhex(hmac_key)

    def verify_signature(
        self,
        signature_header: str,
        payload: str,
        max_age_seconds: int = 300,
    ) -> bool:
        """
        Verify webhook signature.

        Args:
            signature_header: 'Datatrans-Signature' header value
            payload: Raw request body as string
            max_age_seconds: Maximum age of timestamp in seconds

        Returns:
            bool: True if signature is valid

        Raises:
            WebhookVerificationError: If verification fails
        """
        # Parse signature header: t=timestamp,s0=signature
        parts = signature_header.split(",")
        if len(parts) != 2:
            raise WebhookVerificationError("Invalid signature header format")

        timestamp = None
        received_signature = None

        for part in parts:
            if part.startswith("t="):
                timestamp = int(part[2:])
            elif part.startswith("s0="):
                received_signature = part[3:]

        if not timestamp or not received_signature:
            raise WebhookVerificationError("Missing timestamp or signature")

        # Check timestamp age
        current_time = int(time.time() * 1000)
        if abs(current_time - timestamp) > max_age_seconds * 1000:
            raise WebhookVerificationError("Signature timestamp too old")

        # Calculate expected signature
        expected_signature = self._calculate_signature(timestamp, payload)

        # Compare signatures (constant-time comparison)
        if not hmac.compare_digest(expected_signature, received_signature):
            raise WebhookVerificationError("Signature mismatch")

        return True

    def _calculate_signature(self, timestamp: int, payload: str) -> str:
        """Calculate HMAC-SHA256 signature."""
        message = f"{timestamp}{payload}"
        signature = hmac.new(
            self.hmac_key,
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature
