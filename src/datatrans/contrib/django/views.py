import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from datatrans.webhook import WebhookVerifier

from .models import DatatransTransaction

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def webhook_view(request):
    """
    Handle Datatrans webhook notifications.

    Expected URL: POST /datatrans/webhook/
    """
    # Get HMAC key from settings
    hmac_key = getattr(settings, "DATATRANS_HMAC_KEY", None)
    if not hmac_key:
        logger.error("DATATRANS_HMAC_KEY not configured")
        return JsonResponse({"error": "Configuration error"}, status=500)

    # Get signature header
    signature_header = request.headers.get("Datatrans-Signature")
    if not signature_header:
        logger.warning("Missing Datatrans-Signature header")
        return JsonResponse({"error": "Missing signature"}, status=400)

    # Get raw payload
    payload = request.body.decode("utf-8")

    try:
        # Verify signature
        verifier = WebhookVerifier(hmac_key)
        verifier.verify_signature(signature_header, payload)

        # Parse payload
        data = json.loads(payload)
        transaction_id = data.get("transactionId")

        if not transaction_id:
            logger.error("Missing transactionId in webhook payload")
            return JsonResponse({"error": "Invalid payload"}, status=400)

        # Find or create transaction
        try:
            transaction = DatatransTransaction.objects.get(
                transaction_id=transaction_id
            )
        except DatatransTransaction.DoesNotExist:
            logger.warning(f"Transaction {transaction_id} not found in database")
            # Optionally create a new record
            transaction = DatatransTransaction(
                transaction_id=transaction_id, status="initialized"
            )

        # Update transaction based on status
        status = data.get("status")
        if status:
            transaction.update_status(status, data)

            # Update other fields
            transaction.amount = data.get("amount", transaction.amount)
            transaction.currency = data.get("currency", transaction.currency)
            transaction.payment_method = data.get(
                "paymentMethod", transaction.payment_method
            )

            if "card" in data:
                transaction.masked_card = data["card"].get("masked")

            transaction.save()

            # Trigger signals or additional processing
            logger.info(f"Updated transaction {transaction_id} to status {status}")

        return JsonResponse({"status": "received"})

    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return JsonResponse({"error": "Processing error"}, status=500)
