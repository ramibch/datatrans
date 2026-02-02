import base64
import json
import ssl
import urllib.error
import urllib.request
from typing import Dict, Optional

from .exceptions import DatatransError
from .models import (
    AliasInfoResponse,
    AliasPatchRequest,
    AliasPatchResponse,
    AuthorizeRequest,
    AuthorizeResponse,
    AuthorizeSplitRequest,
    AuthorizeSplitResponse,
    CreditRequest,
    DccRequest,
    DccResponse,
    IncreaseRequest,
    InitRequest,
    InitResponse,
    ScreenRequest,
    ScreenResponse,
    SecureFieldsInitRequest,
    SecureFieldsInitResponse,
    SettleRequest,
    StatusResponse,
    ValidateRequest,
    ValidateResponse,
)


class DatatransClient:
    """Main client for Datatrans API interactions."""

    SANDBOX_URL = "https://api.sandbox.datatrans.com"
    PRODUCTION_URL = "https://api.datatrans.com"

    def __init__(self, merchant_id: str, password: str, sandbox: bool = True):
        self.merchant_id = merchant_id
        self.password = password
        self.base_url = self.SANDBOX_URL if sandbox else self.PRODUCTION_URL
        self.auth_header = self._create_auth_header()

    def _create_auth_header(self) -> str:
        """Create Basic Auth header."""
        credentials = f"{self.merchant_id}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict:
        """Make authenticated request to Datatrans API using standard library only."""
        url = f"{self.base_url}{endpoint}"

        # Prepare headers
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
            "User-Agent": "Datatrans-Python/1.0.0",
        }

        if idempotency_key and method.upper() == "POST":
            headers["Idempotency-Key"] = idempotency_key

        # Prepare request data
        body = None
        if data is not None:
            body = json.dumps(data).encode("utf-8")

        # Create request
        req = urllib.request.Request(
            url, data=body, headers=headers, method=method.upper()
        )

        try:
            # Create SSL context with TLS 1.2+ as required by Datatrans
            ssl_context = ssl.create_default_context()
            ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

            # Make the request
            with urllib.request.urlopen(
                req, timeout=30, context=ssl_context
            ) as response:
                response_body = response.read()
                status_code = response.getcode()

                # Parse JSON response if available
                if response_body:
                    try:
                        response_data = json.loads(response_body.decode("utf-8"))
                    except json.JSONDecodeError:
                        # If not JSON, return as text
                        response_data = {"raw_response": response_body.decode("utf-8")}
                else:
                    response_data = {}

                # Check for error status codes
                if status_code >= 400:
                    raise DatatransError(
                        f"API Error {status_code}", status_code, response_data
                    )

                return response_data

        except urllib.error.HTTPError as e:
            # Handle HTTP errors
            error_body = None
            try:
                error_body = e.read()
                if error_body:
                    error_data = json.loads(error_body.decode("utf-8"))
                else:
                    error_data = {}
            except (json.JSONDecodeError, AttributeError):
                error_data = {"raw_error": str(e)}

            raise DatatransError(f"HTTP Error {e.code}: {e.reason}", e.code, error_data)

        except urllib.error.URLError as e:
            # Handle URL errors (connection, timeout, etc.)
            raise DatatransError(
                f"URL Error: {str(e.reason) if e.reason else 'Unknown URL error'}",
                0,
                {"reason": str(e.reason) if e.reason else "Unknown"},
            )

        except ssl.SSLError as e:
            # Handle SSL/TLS errors
            raise DatatransError(f"SSL Error: {str(e)}", 0, {"ssl_error": str(e)})

        except TimeoutError as e:
            # Handle timeout errors
            raise DatatransError(f"Request timeout: {str(e)}", 0, {"timeout": True})

        except Exception as e:
            # Handle any other exceptions
            raise DatatransError(
                f"Request failed: {str(e)}", 0, {"exception_type": type(e).__name__}
            )

    # Transaction Operations
    def init_transaction(
        self, request: InitRequest, idempotency_key: Optional[str] = None
    ) -> InitResponse:
        """Initialize a transaction for Redirect/Lightbox."""
        endpoint = "/v1/transactions"
        response = self._request("POST", endpoint, request.dict(), idempotency_key)
        return InitResponse(**response)

    def secure_fields_init(
        self, request: SecureFieldsInitRequest, idempotency_key: Optional[str] = None
    ) -> SecureFieldsInitResponse:
        """Initialize a Secure Fields transaction."""
        endpoint = "/v1/transactions/secureFields"
        response = self._request("POST", endpoint, request.dict(), idempotency_key)
        return SecureFieldsInitResponse(**response)

    def authorize(
        self, request: AuthorizeRequest, idempotency_key: Optional[str] = None
    ) -> AuthorizeResponse:
        """Authorize a merchant-initiated transaction."""
        endpoint = "/v1/transactions/authorize"
        response = self._request("POST", endpoint, request.dict(), idempotency_key)
        return AuthorizeResponse(**response)

    def authorize_split(
        self, transaction_id: str, request: AuthorizeSplitRequest
    ) -> AuthorizeSplitResponse:
        """Authorize an authenticated transaction."""
        endpoint = f"/v1/transactions/{transaction_id}/authorize-split"
        response = self._request("POST", endpoint, request.dict())
        return AuthorizeSplitResponse(**response)

    def validate_alias(self, request: ValidateRequest) -> ValidateResponse:
        """Validate an existing alias."""
        endpoint = "/v1/transactions/validate"
        response = self._request("POST", endpoint, request.dict())
        return ValidateResponse(**response)

    def get_status(self, transaction_id: str) -> StatusResponse:
        """Check transaction status."""
        endpoint = f"/v1/transactions/{transaction_id}/status"
        response = self._request("GET", endpoint)
        return StatusResponse(**response)

    def settle(self, transaction_id: str, request: SettleRequest) -> Dict:
        """Settle a transaction."""
        endpoint = f"/v1/transactions/{transaction_id}/settle"
        return self._request("POST", endpoint, request.dict())

    def cancel(self, transaction_id: str, request: Optional[Dict] = None) -> Dict:
        """Cancel a transaction."""
        endpoint = f"/v1/transactions/{transaction_id}/cancel"
        return self._request("POST", endpoint, request or {})

    def refund(self, transaction_id: str, request: CreditRequest) -> Dict:
        """Refund a transaction."""
        endpoint = f"/v1/transactions/{transaction_id}/credit"
        return self._request("POST", endpoint, request.dict())

    def increase_amount(self, transaction_id: str, request: IncreaseRequest) -> Dict:
        """Increase authorized amount."""
        endpoint = f"/v1/transactions/{transaction_id}/increase"
        return self._request("POST", endpoint, request.dict())

    # Alias Operations
    def get_alias_info(self, alias: str) -> AliasInfoResponse:
        """Get alias information."""
        endpoint = f"/v1/aliases/{alias}"
        response = self._request("GET", endpoint)
        return AliasInfoResponse(**response)

    def delete_alias(self, alias: str) -> bool:
        """Delete an alias."""
        endpoint = f"/v1/aliases/{alias}"
        try:
            self._request("DELETE", endpoint)
            return True
        except DatatransError:
            return False

    def update_alias(
        self, alias: str, request: AliasPatchRequest
    ) -> AliasPatchResponse:
        """Update alias (patch)."""
        endpoint = f"/v1/aliases/{alias}"
        response = self._request("PATCH", endpoint, request.dict())
        return AliasPatchResponse(**response)

    # DCC Operations
    def get_dcc_options(self, request: DccRequest) -> DccResponse:
        """Get DCC values for a card."""
        endpoint = "/v1/transactions/dcc"
        response = self._request("POST", endpoint, request.dict())
        return DccResponse(**response)

    # Screen Operation
    def screen_customer(self, request: ScreenRequest) -> ScreenResponse:
        """Screen customer details."""
        endpoint = "/v1/transactions/screen"
        response = self._request("POST", endpoint, request.dict())
        return ScreenResponse(**response)

    # Helper Methods
    def generate_redirect_url(self, transaction_id: str) -> str:
        """Generate redirect URL for payment page."""
        base = self.base_url.replace("api", "pay")
        return f"{base}/v1/start/{transaction_id}"

    def generate_lightbox_script(
        self, transaction_id: str, button_id: str = "payButton"
    ) -> str:
        """Generate Lightbox JavaScript snippet."""
        base = self.base_url.replace("api", "pay")
        return f"""
        <script src="{base}/upp/payment/js/datatrans-2.0.0.js"></script>
        <script>
            document.getElementById('{button_id}').onclick = function() {{
                Datatrans.startPayment({{
                    transactionId: "{transaction_id}"
                }});
            }};
        </script>
        """
