class DatatransError(Exception):
    """Base exception for Datatrans API errors."""

    def __init__(self, message: str, status_code: int, error_data: dict):
        self.message = message
        self.status_code = status_code
        self.error_data = error_data
        super().__init__(f"{message} (Status: {status_code})")


class WebhookVerificationError(Exception):
    """Exception for webhook signature verification failures."""

    pass


class ConfigurationError(Exception):
    """Exception for configuration issues."""

    pass
