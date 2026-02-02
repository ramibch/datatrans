"""
Data models for Datatrans API requests and responses.
Pure Python implementation with no external dependencies.
"""

import datetime
import json
import re
from enum import Enum
from typing import Any, Dict, List, Optional

# ============== VALIDATION UTILITIES ==============


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


def validate_regex(value: str, pattern: str, field_name: str):
    """Validate string against regex pattern."""
    if value and not re.match(pattern, value):
        raise ValidationError(f"{field_name} must match pattern {pattern}")


def validate_length(value: str, min_len: int, max_len: int, field_name: str):
    """Validate string length."""
    if value is not None:
        length = len(value)
        if length < min_len or length > max_len:
            raise ValidationError(
                f"{field_name} must be between {min_len} and {max_len} characters"
            )


def validate_card_number(number: str):
    """Validate card number using Luhn algorithm."""
    if not number or not number.isdigit():
        raise ValidationError("Card number must contain only digits")

    # Luhn algorithm
    total = 0
    reverse_digits = number[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n

    if total % 10 != 0:
        raise ValidationError("Invalid card number")


def validate_expiry_month(month: str):
    """Validate expiry month (01-12)."""
    if month:
        if not re.match(r"^\d{2}$", month):
            raise ValidationError("Expiry month must be 2 digits")
        m = int(month)
        if m < 1 or m > 12:
            raise ValidationError("Expiry month must be between 01 and 12")


def validate_amount(amount: int):
    """Validate amount is positive."""
    if amount is not None and amount <= 0:
        raise ValidationError("Amount must be positive")


# ============== ENUMS ==============


class PaymentMethod(str, Enum):
    VISA = "VIS"
    MASTERCARD = "ECA"
    AMEX = "AMX"
    PAYPAL = "PAP"
    TWINT = "TWI"
    POSTFINANCE_CARD = "PFC"
    KLARNA = "KLN"
    APPLE_PAY = "APL"
    GOOGLE_PAY = "PAY"
    ALIPAY = "ALP"
    SWISH = "SWH"
    VIPPS = "VPS"
    MOBILEPAY = "MBP"
    POSTFINANCE_PAY = "PFP"


class TransactionType(str, Enum):
    PAYMENT = "payment"
    CREDIT = "credit"
    CARD_CHECK = "card_check"


class TransactionStatus(str, Enum):
    INITIALIZED = "initialized"
    AUTHORIZED = "authorized"
    SETTLED = "settled"
    CANCELED = "canceled"
    FAILED = "failed"
    REFUNDED = "refunded"
    COMPENSATED = "compensated"
    TRANSMITTED = "transmitted"


class Language(str, Enum):
    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    ITALIAN = "it"
    SPANISH = "es"
    GREEK = "el"
    FINNISH = "fi"
    HUNGARIAN = "hu"
    KOREAN = "ko"
    DUTCH = "nl"
    NORWEGIAN = "no"
    DANISH = "da"
    POLISH = "pl"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    JAPANESE = "ja"
    SLOVAK = "sk"
    SLOVENIAN = "sl"
    SWEDISH = "sv"
    TURKISH = "tr"
    CHINESE = "zh"


class CardType(str, Enum):
    PLAIN = "PLAIN"
    ALIAS = "ALIAS"
    NETWORK_TOKEN = "NETWORK_TOKEN"
    DEVICE_TOKEN = "DEVICE_TOKEN"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


# ============== BASE MODEL CLASS ==============


class BaseModel:
    """Base class for all models with serialization and validation."""

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if exclude_none and value is None:
                continue

            # Handle nested BaseModel instances
            if isinstance(value, BaseModel):
                result[key] = value.to_dict(exclude_none)
            # Handle lists of BaseModel instances
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict(exclude_none) if isinstance(item, BaseModel) else item
                    for item in value
                ]
            # Handle enums
            elif isinstance(value, Enum):
                result[key] = value.value
            # Handle datetime
            elif isinstance(value, datetime.datetime):
                result[key] = value.isoformat()
            # Handle regular values
            else:
                result[key] = value

        return result

    def to_json(self, exclude_none: bool = False, indent: Optional[int] = None) -> str:
        """Convert model to JSON string."""
        return json.dumps(self.to_dict(exclude_none), indent=indent, default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """Create model instance from dictionary."""
        # This should be overridden by subclasses for proper validation
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance

    def validate(self):
        """Validate model data. Should be overridden by subclasses."""
        pass

    def __str__(self):
        return self.to_json(exclude_none=True)


# ============== COMMON MODELS ==============


class Address(BaseModel):
    """Common address model."""

    def __init__(
        self,
        street: Optional[str] = None,
        street2: Optional[str] = None,
        city: Optional[str] = None,
        zipCode: Optional[str] = None,
        country: Optional[str] = None,
        state: Optional[str] = None,
    ):
        self.street = street
        self.street2 = street2
        self.city = city
        self.zipCode = zipCode
        self.country = country
        self.state = state

    def validate(self):
        validate_length(self.street, 0, 100, "street")
        validate_length(self.street2, 0, 100, "street2")
        validate_length(self.city, 0, 100, "city")
        validate_length(self.zipCode, 0, 20, "zipCode")
        validate_length(self.country, 0, 2, "country")
        validate_length(self.state, 0, 100, "state")


class CustomerRequest(BaseModel):
    """Customer information."""

    def __init__(
        self,
        id: Optional[str] = None,
        title: Optional[str] = None,
        firstName: Optional[str] = None,
        lastName: Optional[str] = None,
        birthDate: Optional[str] = None,
        gender: Optional[Gender] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        cellPhone: Optional[str] = None,
        language: Optional[str] = None,
        type: Optional[str] = None,
        ipAddress: Optional[str] = None,
    ):
        self.id = id
        self.title = title
        self.firstName = firstName
        self.lastName = lastName
        self.birthDate = birthDate
        self.gender = gender
        self.email = email
        self.phone = phone
        self.cellPhone = cellPhone
        self.language = language
        self.type = type
        self.ipAddress = ipAddress

    def validate(self):
        validate_length(self.id, 0, 100, "id")
        validate_length(self.title, 0, 50, "title")
        validate_length(self.firstName, 0, 100, "firstName")
        validate_length(self.lastName, 0, 100, "lastName")
        validate_length(self.email, 0, 255, "email")
        validate_length(self.phone, 0, 50, "phone")
        validate_length(self.cellPhone, 0, 50, "cellPhone")
        validate_length(self.language, 0, 2, "language")
        validate_length(self.type, 0, 1, "type")
        validate_length(self.ipAddress, 0, 45, "ipAddress")

        # Validate birth date format
        if self.birthDate:
            try:
                datetime.datetime.strptime(self.birthDate, "%Y-%m-%d")
            except ValueError:
                raise ValidationError("birthDate must be in YYYY-MM-DD format")


class BillingAddress(Address):
    """Billing address."""

    pass


class ShippingAddress(Address):
    """Shipping address."""

    pass


class Article(BaseModel):
    """Order article/item."""

    def __init__(
        self,
        code: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        quantity: Optional[int] = 1,
        amount: Optional[int] = None,
        vat: Optional[float] = None,
        vatAmount: Optional[int] = None,
        imageUrl: Optional[str] = None,
    ):
        self.code = code
        self.name = name
        self.description = description
        self.quantity = quantity
        self.amount = amount
        self.vat = vat
        self.vatAmount = vatAmount
        self.imageUrl = imageUrl

    def validate(self):
        validate_length(self.code, 0, 100, "code")
        validate_length(self.name, 0, 100, "name")
        validate_length(self.description, 0, 500, "description")
        validate_length(self.imageUrl, 0, 2000, "imageUrl")

        if self.quantity is not None and self.quantity <= 0:
            raise ValidationError("quantity must be positive")

        if self.amount is not None:
            validate_amount(self.amount)

        if self.vat is not None and self.vat < 0:
            raise ValidationError("vat cannot be negative")

        if self.vatAmount is not None:
            validate_amount(self.vatAmount)


class OrderRequest(BaseModel):
    """Order information."""

    def __init__(self, articles: Optional[List[Article]] = None):
        self.articles = articles or []

    def validate(self):
        for article in self.articles:
            if isinstance(article, dict):
                article = Article.from_dict(article)
            article.validate()

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        result = super().to_dict(exclude_none)
        if self.articles:
            result["articles"] = [
                article.to_dict(exclude_none)
                if isinstance(article, BaseModel)
                else article
                for article in self.articles
            ]
        return result


class RedirectRequest(BaseModel):
    """Redirect URLs for payment page."""

    def __init__(
        self,
        successUrl: Optional[str] = None,
        cancelUrl: Optional[str] = None,
        errorUrl: Optional[str] = None,
    ):
        self.successUrl = successUrl
        self.cancelUrl = cancelUrl
        self.errorUrl = errorUrl

    def validate(self):
        validate_length(self.successUrl, 0, 4000, "successUrl")
        validate_length(self.cancelUrl, 0, 4000, "cancelUrl")
        validate_length(self.errorUrl, 0, 4000, "errorUrl")


class WebhookRequest(BaseModel):
    """Webhook configuration."""

    def __init__(self, url: Optional[str] = None, method: Optional[str] = "POST"):
        self.url = url
        self.method = method

    def validate(self):
        validate_length(self.url, 0, 4000, "url")
        if self.method and self.method not in ["GET", "POST"]:
            raise ValidationError("method must be GET or POST")


class ThreeDSecure(BaseModel):
    """3D Secure parameters."""

    def __init__(
        self,
        challengeIndicator: Optional[str] = None,
        exemption: Optional[str] = None,
        threeDSTransactionId: Optional[str] = None,
        authenticationResponse: Optional[str] = None,
        transStatusReason: Optional[str] = None,
        cardholderInfo: Optional[str] = None,
        messageExtensions: Optional[List[Dict[str, Any]]] = None,
    ):
        self.challengeIndicator = challengeIndicator
        self.exemption = exemption
        self.threeDSTransactionId = threeDSTransactionId
        self.authenticationResponse = authenticationResponse
        self.transStatusReason = transStatusReason
        self.cardholderInfo = cardholderInfo
        self.messageExtensions = messageExtensions


class OptionRequest(BaseModel):
    """Options for transaction initialization."""

    def __init__(
        self,
        createAlias: Optional[bool] = False,
        authenticateOnly: Optional[bool] = False,
        returnMobileToken: Optional[bool] = False,
        rememberMe: Optional[bool] = False,
        storeCustomerData: Optional[bool] = False,
    ):
        self.createAlias = createAlias
        self.authenticateOnly = authenticateOnly
        self.returnMobileToken = returnMobileToken
        self.rememberMe = rememberMe
        self.storeCustomerData = storeCustomerData


class AuthorizeOptionRequest(OptionRequest):
    """Options for authorization."""

    pass


class Metadata(BaseModel):
    """Merchant reference data."""

    def __init__(self, custom: Optional[Dict[str, Any]] = None):
        self.custom = custom or {}


class CardInfo(BaseModel):
    """Card information."""

    def __init__(
        self,
        brand: Optional[str] = None,
        type: Optional[str] = None,
        usage: Optional[str] = None,
        country: Optional[str] = None,
        issuer: Optional[str] = None,
    ):
        self.brand = brand
        self.type = type
        self.usage = usage
        self.country = country
        self.issuer = issuer


class DccOption(BaseModel):
    """Dynamic Currency Conversion option."""

    def __init__(self, amount: int, currency: str, exponent: int = 2):
        self.amount = amount
        self.currency = currency
        self.exponent = exponent

    def validate(self):
        validate_amount(self.amount)
        validate_length(self.currency, 3, 3, "currency")
        if self.exponent < 0:
            raise ValidationError("exponent cannot be negative")


class CardHolderData(BaseModel):
    """Cardholder data for tokenization."""

    def __init__(
        self,
        ipAddress: Optional[str] = None,
        phoneNumber: Optional[str] = None,
        emailAddress: Optional[str] = None,
    ):
        self.ipAddress = ipAddress
        self.phoneNumber = phoneNumber
        self.emailAddress = emailAddress


class CardOnFile(BaseModel):
    """Card On File parameters."""

    def __init__(
        self, transaction: Optional[str] = None, agreement: Optional[str] = None
    ):
        self.transaction = transaction
        self.agreement = agreement

    def validate(self):
        valid_transactions = ["FIRST", "SUBSEQUENT", "RESUBMISSION"]
        valid_agreements = ["RECURRING", "INSTALLMENT", "UNSCHEDULED"]

        if self.transaction and self.transaction not in valid_transactions:
            raise ValidationError(f"transaction must be one of {valid_transactions}")

        if self.agreement and self.agreement not in valid_agreements:
            raise ValidationError(f"agreement must be one of {valid_agreements}")


class NetworkTokenOptions(BaseModel):
    """Network tokenization options."""

    def __init__(self, createNetworkToken: Optional[bool] = False):
        self.createNetworkToken = createNetworkToken


# ============== CARD MODELS ==============


class BaseCard(BaseModel):
    """Base card model."""

    def __init__(
        self,
        expiryMonth: Optional[str] = None,
        expiryYear: Optional[str] = None,
        cardholder: Optional[CardHolderData] = None,
        cardOnFile: Optional[CardOnFile] = None,
    ):
        self.expiryMonth = expiryMonth
        self.expiryYear = expiryYear
        self.cardholder = cardholder
        self.cardOnFile = cardOnFile

    def validate_base(self):
        validate_expiry_month(self.expiryMonth)
        validate_regex(self.expiryYear, r"^\d{2}$", "expiryYear")

        if self.cardholder:
            if isinstance(self.cardholder, dict):
                self.cardholder = CardHolderData.from_dict(self.cardholder)
            self.cardholder.validate()

        if self.cardOnFile:
            if isinstance(self.cardOnFile, dict):
                self.cardOnFile = CardOnFile.from_dict(self.cardOnFile)
            self.cardOnFile.validate()


class PlainCard(BaseCard):
    """Plain card (card number)."""

    def __init__(self, number: str, cvv: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.type = CardType.PLAIN
        self.number = number
        self.cvv = cvv

    def validate(self):
        self.validate_base()
        validate_card_number(self.number)
        validate_length(self.number, 12, 19, "number")
        if self.cvv:
            validate_length(self.cvv, 3, 4, "cvv")
            if not self.cvv.isdigit():
                raise ValidationError("CVV must contain only digits")


class AliasCard(BaseCard):
    """Alias card."""

    def __init__(self, alias: str, **kwargs):
        super().__init__(**kwargs)
        self.type = CardType.ALIAS
        self.alias = alias

    def validate(self):
        self.validate_base()
        validate_length(self.alias, 10, 100, "alias")


class NetworkTokenCard(BaseCard):
    """Network token card."""

    def __init__(
        self,
        token: str,
        expiryMonth: str,
        expiryYear: str,
        cvv: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.type = CardType.NETWORK_TOKEN
        self.token = token
        self.expiryMonth = expiryMonth
        self.expiryYear = expiryYear
        self.cvv = cvv

    def validate(self):
        self.validate_base()
        validate_length(self.token, 0, 100, "token")
        validate_expiry_month(self.expiryMonth)
        validate_regex(self.expiryYear, r"^\d{2}$", "expiryYear")
        if self.cvv:
            validate_length(self.cvv, 3, 4, "cvv")


class DeviceTokenCard(BaseCard):
    """Device token card (Apple Pay/Google Pay)."""

    def __init__(self, token: str, cvv: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.type = CardType.DEVICE_TOKEN
        self.token = token
        self.cvv = cvv

    def validate(self):
        self.validate_base()
        validate_length(self.token, 0, 2000, "token")
        if self.cvv:
            validate_length(self.cvv, 3, 4, "cvv")


# ============== REQUEST MODELS ==============


class InitRequest(BaseModel):
    """Initialize transaction request."""

    def __init__(
        self,
        currency: str,
        refno: str,
        amount: Optional[int] = None,
        refno2: Optional[str] = None,
        customer: Optional[CustomerRequest] = None,
        billing: Optional[BillingAddress] = None,
        shipping: Optional[ShippingAddress] = None,
        order: Optional[OrderRequest] = None,
        autoSettle: Optional[bool] = None,
        option: Optional[OptionRequest] = None,
        language: Optional[Language] = None,
        redirect: Optional[RedirectRequest] = None,
        webhook: Optional[WebhookRequest] = None,
        paymentMethods: Optional[List[PaymentMethod]] = None,
        card: Optional[BaseCard] = None,
        PAP: Optional[Dict[str, Any]] = None,
        TWI: Optional[Dict[str, Any]] = None,
        KLN: Optional[Dict[str, Any]] = None,
        PFC: Optional[Dict[str, Any]] = None,
        mcp: Optional[Dict[str, Any]] = None,
        dcc: Optional[Dict[str, Any]] = None,
        airlineData: Optional[Dict[str, Any]] = None,
        metadata: Optional[Metadata] = None,
    ):
        self.amount = amount
        self.currency = currency
        self.refno = refno
        self.refno2 = refno2
        self.customer = customer
        self.billing = billing
        self.shipping = shipping
        self.order = order
        self.autoSettle = autoSettle
        self.option = option
        self.language = language
        self.redirect = redirect
        self.webhook = webhook
        self.paymentMethods = paymentMethods
        self.card = card
        self.PAP = PAP
        self.TWI = TWI
        self.KLN = KLN
        self.PFC = PFC
        self.mcp = mcp
        self.dcc = dcc
        self.airlineData = airlineData
        self.metadata = metadata

    def validate(self):
        if self.amount is not None:
            validate_amount(self.amount)

        validate_length(self.currency, 3, 3, "currency")
        validate_length(self.refno, 1, 40, "refno")
        validate_length(self.refno2, 0, 40, "refno2")

        if self.customer:
            if isinstance(self.customer, dict):
                self.customer = CustomerRequest.from_dict(self.customer)
            self.customer.validate()

        if self.billing:
            if isinstance(self.billing, dict):
                self.billing = BillingAddress.from_dict(self.billing)
            self.billing.validate()

        if self.shipping:
            if isinstance(self.shipping, dict):
                self.shipping = ShippingAddress.from_dict(self.shipping)
            self.shipping.validate()

        if self.order:
            if isinstance(self.order, dict):
                self.order = OrderRequest.from_dict(self.order)
            self.order.validate()

        if self.redirect:
            if isinstance(self.redirect, dict):
                self.redirect = RedirectRequest.from_dict(self.redirect)
            self.redirect.validate()

        if self.webhook:
            if isinstance(self.webhook, dict):
                self.webhook = WebhookRequest.from_dict(self.webhook)
            self.webhook.validate()

        if self.card:
            self._validate_card(self.card)

        if self.metadata:
            if isinstance(self.metadata, dict):
                self.metadata = Metadata.from_dict(self.metadata)

    def _validate_card(self, card_data):
        """Validate card based on type."""
        if isinstance(card_data, dict):
            card_type = card_data.get("type")
            if card_type == CardType.PLAIN.value:
                card = PlainCard.from_dict(card_data)
            elif card_type == CardType.ALIAS.value:
                card = AliasCard.from_dict(card_data)
            elif card_type == CardType.NETWORK_TOKEN.value:
                card = NetworkTokenCard.from_dict(card_data)
            elif card_type == CardType.DEVICE_TOKEN.value:
                card = DeviceTokenCard.from_dict(card_data)
            else:
                raise ValidationError(f"Unknown card type: {card_type}")
            card.validate()
            self.card = card
        elif isinstance(card_data, BaseCard):
            card_data.validate()
        else:
            raise ValidationError("card must be a dictionary or BaseCard instance")


class SecureFieldsInitRequest(BaseModel):
    """Initialize Secure Fields transaction."""

    def __init__(
        self,
        currency: str,
        returnUrl: str,
        amount: int,
        returnResources: Optional[bool] = False,
        returnMethod: Optional[str] = "POST",
        mcp: Optional[Dict[str, Any]] = None,
        threeD: Optional[ThreeDSecure] = None,
    ):
        self.returnResources = returnResources
        self.amount = amount
        self.currency = currency
        self.returnUrl = returnUrl
        self.returnMethod = returnMethod
        self.mcp = mcp
        self.threeD = threeD

    def validate(self):
        validate_amount(self.amount)
        validate_length(self.currency, 3, 3, "currency")
        validate_length(self.returnUrl, 1, 4000, "returnUrl")

        if self.returnMethod and self.returnMethod not in ["GET", "POST"]:
            raise ValidationError("returnMethod must be GET or POST")

        if self.threeD:
            if isinstance(self.threeD, dict):
                self.threeD = ThreeDSecure.from_dict(self.threeD)


class AuthorizeRequest(BaseModel):
    """Authorize transaction request."""

    def __init__(
        self,
        amount: int,
        currency: str,
        refno: str,
        refno2: Optional[str] = None,
        customer: Optional[CustomerRequest] = None,
        billing: Optional[BillingAddress] = None,
        shipping: Optional[ShippingAddress] = None,
        order: Optional[OrderRequest] = None,
        autoSettle: Optional[bool] = None,
        option: Optional[AuthorizeOptionRequest] = None,
        card: Optional[BaseCard] = None,
        PAP: Optional[Dict[str, Any]] = None,
        TWI: Optional[Dict[str, Any]] = None,
        KLN: Optional[Dict[str, Any]] = None,
        mcp: Optional[Dict[str, Any]] = None,
        dcc: Optional[Dict[str, Any]] = None,
        airlineData: Optional[Dict[str, Any]] = None,
        metadata: Optional[Metadata] = None,
    ):
        self.amount = amount
        self.currency = currency
        self.refno = refno
        self.refno2 = refno2
        self.customer = customer
        self.billing = billing
        self.shipping = shipping
        self.order = order
        self.autoSettle = autoSettle
        self.option = option
        self.card = card
        self.PAP = PAP
        self.TWI = TWI
        self.KLN = KLN
        self.mcp = mcp
        self.dcc = dcc
        self.airlineData = airlineData
        self.metadata = metadata

    def validate(self):
        validate_amount(self.amount)
        validate_length(self.currency, 3, 3, "currency")
        validate_length(self.refno, 1, 40, "refno")
        validate_length(self.refno2, 0, 40, "refno2")

        if self.card:
            # Reuse validation from InitRequest
            init_req = InitRequest(currency=self.currency, refno=self.refno)
            init_req._validate_card(self.card)

        if self.option:
            if isinstance(self.option, dict):
                self.option = AuthorizeOptionRequest.from_dict(self.option)


class AuthorizeSplitRequest(BaseModel):
    """Authorize authenticated transaction."""

    def __init__(
        self,
        refno: str,
        amount: Optional[int] = None,
        refno2: Optional[str] = None,
        autoSettle: Optional[bool] = None,
        airlineData: Optional[Dict[str, Any]] = None,
        threeD: Optional[ThreeDSecure] = None,
    ):
        self.amount = amount
        self.refno = refno
        self.refno2 = refno2
        self.autoSettle = autoSettle
        self.airlineData = airlineData
        self.threeD = threeD

    def validate(self):
        if self.amount is not None:
            validate_amount(self.amount)
        validate_length(self.refno, 0, 40, "refno")
        validate_length(self.refno2, 0, 40, "refno2")


class ValidateRequest(BaseModel):
    """Validate alias request."""

    def __init__(
        self,
        refno: str,
        currency: str,
        refno2: Optional[str] = None,
        card: Optional[BaseCard] = None,
        PFC: Optional[Dict[str, Any]] = None,
        KLN: Optional[Dict[str, Any]] = None,
        PAP: Optional[Dict[str, Any]] = None,
    ):
        self.refno = refno
        self.refno2 = refno2
        self.currency = currency
        self.card = card
        self.PFC = PFC
        self.KLN = KLN
        self.PAP = PAP

    def validate(self):
        validate_length(self.refno, 1, 40, "refno")
        validate_length(self.refno2, 0, 40, "refno2")
        validate_length(self.currency, 3, 3, "currency")

        if self.card:
            init_req = InitRequest(currency=self.currency, refno=self.refno)
            init_req._validate_card(self.card)


class SettleRequest(BaseModel):
    """Settle transaction request."""

    def __init__(
        self,
        amount: int,
        currency: str,
        refno: str,
        refno2: Optional[str] = None,
        airlineData: Optional[Dict[str, Any]] = None,
        mcp: Optional[Dict[str, Any]] = None,
        partialCapture: Optional[Dict[str, Any]] = None,
        extensions: Optional[Dict[str, Any]] = None,
        order: Optional[OrderRequest] = None,
    ):
        self.amount = amount
        self.currency = currency
        self.refno = refno
        self.refno2 = refno2
        self.airlineData = airlineData
        self.mcp = mcp
        self.partialCapture = partialCapture
        self.extensions = extensions
        self.order = order

    def validate(self):
        validate_amount(self.amount)
        validate_length(self.currency, 3, 3, "currency")
        validate_length(self.refno, 1, 40, "refno")
        validate_length(self.refno2, 0, 40, "refno2")

        if self.order:
            if isinstance(self.order, dict):
                self.order = OrderRequest.from_dict(self.order)
            self.order.validate()


class CreditRequest(BaseModel):
    """Credit/refund request."""

    def __init__(
        self,
        currency: str,
        refno: str,
        amount: Optional[int] = None,
        refno2: Optional[str] = None,
        airlineData: Optional[Dict[str, Any]] = None,
        marketplace: Optional[Dict[str, Any]] = None,
        extensions: Optional[Dict[str, Any]] = None,
        mcp: Optional[Dict[str, Any]] = None,
        metadata: Optional[Metadata] = None,
        order: Optional[OrderRequest] = None,
    ):
        self.amount = amount
        self.currency = currency
        self.refno = refno
        self.refno2 = refno2
        self.airlineData = airlineData
        self.marketplace = marketplace
        self.extensions = extensions
        self.mcp = mcp
        self.metadata = metadata
        self.order = order

    def validate(self):
        if self.amount is not None:
            validate_amount(self.amount)
        validate_length(self.currency, 3, 3, "currency")
        validate_length(self.refno, 1, 40, "refno")
        validate_length(self.refno2, 0, 40, "refno2")

        if self.metadata:
            if isinstance(self.metadata, dict):
                self.metadata = Metadata.from_dict(self.metadata)

        if self.order:
            if isinstance(self.order, dict):
                self.order = OrderRequest.from_dict(self.order)
            self.order.validate()


class IncreaseRequest(BaseModel):
    """Increase authorization amount request."""

    def __init__(
        self,
        amount: int,
        currency: str,
        refno: str,
        metadata: Optional[Metadata] = None,
    ):
        self.amount = amount
        self.currency = currency
        self.refno = refno
        self.metadata = metadata

    def validate(self):
        validate_amount(self.amount)
        validate_length(self.currency, 3, 3, "currency")
        validate_length(self.refno, 1, 40, "refno")

        if self.metadata:
            if isinstance(self.metadata, dict):
                self.metadata = Metadata.from_dict(self.metadata)


class ScreenRequest(BaseModel):
    """Screen customer request."""

    def __init__(
        self,
        amount: int,
        currency: str,
        refno: str,
        customer: Optional[CustomerRequest] = None,
        billing: Optional[BillingAddress] = None,
        shipping: Optional[ShippingAddress] = None,
        INT: Optional[Dict[str, Any]] = None,
        MFA: Optional[Dict[str, Any]] = None,
        DVI: Optional[Dict[str, Any]] = None,
    ):
        self.amount = amount
        self.currency = currency
        self.refno = refno
        self.customer = customer
        self.billing = billing
        self.shipping = shipping
        self.INT = INT
        self.MFA = MFA
        self.DVI = DVI

    def validate(self):
        validate_amount(self.amount)
        validate_length(self.currency, 3, 3, "currency")
        validate_length(self.refno, 1, 40, "refno")

        if self.customer:
            if isinstance(self.customer, dict):
                self.customer = CustomerRequest.from_dict(self.customer)
            self.customer.validate()

        if self.billing:
            if isinstance(self.billing, dict):
                self.billing = BillingAddress.from_dict(self.billing)
            self.billing.validate()

        if self.shipping:
            if isinstance(self.shipping, dict):
                self.shipping = ShippingAddress.from_dict(self.shipping)
            self.shipping.validate()


class DccRequest(BaseModel):
    """DCC request."""

    def __init__(
        self,
        type: CardType,
        currency: str,
        amount: int,
        cardNumber: Optional[str] = None,
        alias: Optional[str] = None,
    ):
        self.type = type
        self.cardNumber = cardNumber
        self.alias = alias
        self.currency = currency
        self.amount = amount

    def validate(self):
        validate_amount(self.amount)
        validate_length(self.currency, 3, 3, "currency")

        if self.type == CardType.PLAIN:
            if not self.cardNumber:
                raise ValidationError("cardNumber is required for PLAIN card type")
            validate_card_number(self.cardNumber)
        elif self.type == CardType.ALIAS:
            if not self.alias:
                raise ValidationError("alias is required for ALIAS card type")
            validate_length(self.alias, 10, 100, "alias")


# ============== ALIAS MODELS ==============


class AliasPatchRequest(BaseModel):
    """Patch alias request."""

    def __init__(
        self,
        removePlain: Optional[bool] = False,
        expiryMonth: Optional[str] = None,
        expiryYear: Optional[str] = None,
        cardholder: Optional[CardHolderData] = None,
        createNetworkToken: Optional[bool] = False,
        cardOnFile: Optional[CardOnFile] = None,
        cardHolderNameVerification: Optional[Dict[str, Any]] = None,
    ):
        self.removePlain = removePlain
        self.expiryMonth = expiryMonth
        self.expiryYear = expiryYear
        self.cardholder = cardholder
        self.createNetworkToken = createNetworkToken
        self.cardOnFile = cardOnFile
        self.cardHolderNameVerification = cardHolderNameVerification

    def validate(self):
        if self.expiryMonth:
            validate_expiry_month(self.expiryMonth)
        if self.expiryYear:
            validate_regex(self.expiryYear, r"^\d{2}$", "expiryYear")

        if self.cardholder:
            if isinstance(self.cardholder, dict):
                self.cardholder = CardHolderData.from_dict(self.cardholder)
            self.cardholder.validate()

        if self.cardOnFile:
            if isinstance(self.cardOnFile, dict):
                self.cardOnFile = CardOnFile.from_dict(self.cardOnFile)
            self.cardOnFile.validate()


class AliasConvertRequest(BaseModel):
    """Convert alias request."""

    def __init__(
        self,
        type: str,
        legacyAlias: str,
        expiryMonth: Optional[str] = None,
        expiryYear: Optional[str] = None,
    ):
        self.type = type
        self.expiryMonth = expiryMonth
        self.expiryYear = expiryYear
        self.legacyAlias = legacyAlias

    def validate(self):
        if not self.type:
            raise ValidationError("type is required")
        if not self.legacyAlias:
            raise ValidationError("legacyAlias is required")

        if self.expiryMonth:
            validate_expiry_month(self.expiryMonth)
        if self.expiryYear:
            validate_regex(self.expiryYear, r"^\d{2}$", "expiryYear")


class TokenizeRequest(BaseModel):
    """Tokenization request."""

    def __init__(
        self,
        type: str,
        pan: Optional[str] = None,
        cvv: Optional[str] = None,
        custom: Optional[str] = None,
        expiryMonth: Optional[str] = None,
        expiryYear: Optional[str] = None,
        cardholder: Optional[CardHolderData] = None,
        networkTokenOptions: Optional[NetworkTokenOptions] = None,
    ):
        self.type = type
        self.pan = pan
        self.cvv = cvv
        self.custom = custom
        self.expiryMonth = expiryMonth
        self.expiryYear = expiryYear
        self.cardholder = cardholder
        self.networkTokenOptions = networkTokenOptions

    def validate(self):
        if self.type == "CARD":
            if not self.pan:
                raise ValidationError("pan is required for CARD type")
            validate_card_number(self.pan)
            if self.expiryMonth:
                validate_expiry_month(self.expiryMonth)
            if self.expiryYear:
                validate_regex(self.expiryYear, r"^\d{2}$", "expiryYear")
        elif self.type == "CVV":
            if not self.cvv:
                raise ValidationError("cvv is required for CVV type")
            if not self.cvv.isdigit():
                raise ValidationError("CVV must contain only digits")
        elif self.type == "CUSTOM":
            if not self.custom:
                raise ValidationError("custom is required for CUSTOM type")
        else:
            raise ValidationError(f"Unknown type: {self.type}")

        if self.cardholder:
            if isinstance(self.cardholder, dict):
                self.cardholder = CardHolderData.from_dict(self.cardholder)
            self.cardholder.validate()

        if self.networkTokenOptions:
            if isinstance(self.networkTokenOptions, dict):
                self.networkTokenOptions = NetworkTokenOptions.from_dict(
                    self.networkTokenOptions
                )


class DetokenizeRequest(BaseModel):
    """Detokenization request."""

    def __init__(self, type: str, alias: str):
        self.type = type
        self.alias = alias

    def validate(self):
        if not self.type:
            raise ValidationError("type is required")
        if not self.alias:
            raise ValidationError("alias is required")

        valid_types = ["CARD", "CVV", "CUSTOM"]
        if self.type not in valid_types:
            raise ValidationError(f"type must be one of {valid_types}")


# ============== RESPONSE MODELS ==============


class ResourceInfo(BaseModel):
    """Resource information with integrity hash."""

    def __init__(self, integrity: str):
        self.integrity = integrity


class BaseResponse(BaseModel):
    """Base response model."""

    def __init__(
        self,
        transactionId: Optional[str] = None,
        error: Optional[Dict[str, Any]] = None,
    ):
        self.transactionId = transactionId
        self.error = error


class InitResponse(BaseResponse):
    """Initialize transaction response."""

    def __init__(self, resources: Optional[List[ResourceInfo]] = None, **kwargs):
        super().__init__(**kwargs)
        self.resources = resources or []

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        result = super().to_dict(exclude_none)
        if self.resources:
            result["resources"] = [
                resource.to_dict(exclude_none)
                if isinstance(resource, BaseModel)
                else resource
                for resource in self.resources
            ]
        return result


class SecureFieldsInitResponse(BaseResponse):
    """Secure Fields init response."""

    def __init__(self, resources: Optional[List[ResourceInfo]] = None, **kwargs):
        super().__init__(**kwargs)
        self.resources = resources or []

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        result = super().to_dict(exclude_none)
        if self.resources:
            result["resources"] = [
                resource.to_dict(exclude_none)
                if isinstance(resource, BaseModel)
                else resource
                for resource in self.resources
            ]
        return result


class AuthorizeResponse(BaseResponse):
    """Authorize response."""

    def __init__(
        self,
        acquirerAuthorizationCode: Optional[str] = None,
        card: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.acquirerAuthorizationCode = acquirerAuthorizationCode
        self.card = card


class AuthorizeSplitResponse(BaseModel):
    """Authorize split response."""

    def __init__(self, acquirerAuthorizationCode: Optional[str] = None):
        self.acquirerAuthorizationCode = acquirerAuthorizationCode


class ValidateResponse(BaseResponse):
    """Validate response."""

    def __init__(
        self,
        acquirerAuthorizationCode: Optional[str] = None,
        card: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.acquirerAuthorizationCode = acquirerAuthorizationCode
        self.card = card


class IncreaseResponse(BaseModel):
    """Increase amount response."""

    def __init__(self, increasedAmount: int):
        self.increasedAmount = increasedAmount

    def validate(self):
        validate_amount(self.increasedAmount)


class ScreenResponse(BaseResponse):
    """Screen response."""

    def __init__(self, INT: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        self.INT = INT


class DccResponse(BaseModel):
    """DCC response."""

    def __init__(
        self,
        dccAvailable: bool,
        originalOption: DccOption,
        dccOption: Optional[DccOption] = None,
        baseRate: Optional[str] = None,
        rate: Optional[float] = None,
        margin: Optional[float] = None,
        correlationId: Optional[str] = None,
    ):
        self.dccAvailable = dccAvailable
        self.originalOption = originalOption
        self.dccOption = dccOption
        self.baseRate = baseRate
        self.rate = rate
        self.margin = margin
        self.correlationId = correlationId

    def validate(self):
        if isinstance(self.originalOption, dict):
            self.originalOption = DccOption.from_dict(self.originalOption)
        self.originalOption.validate()

        if self.dccOption:
            if isinstance(self.dccOption, dict):
                self.dccOption = DccOption.from_dict(self.dccOption)
            self.dccOption.validate()


class StatusDetail(BaseModel):
    """Transaction status detail."""

    def __init__(
        self,
        authorize: Optional[Dict[str, Any]] = None,
        settle: Optional[Dict[str, Any]] = None,
        credit: Optional[Dict[str, Any]] = None,
        cancel: Optional[Dict[str, Any]] = None,
    ):
        self.authorize = authorize
        self.settle = settle
        self.credit = credit
        self.cancel = cancel


class HistoryEntry(BaseModel):
    """Transaction history entry."""

    def __init__(
        self,
        action: str,
        date: Union[str, datetime.datetime],
        source: str,
        success: bool,
        amount: Optional[int] = None,
        ip: Optional[str] = None,
    ):
        self.action = action
        if isinstance(date, str):
            try:
                self.date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
            except ValueError:
                self.date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        else:
            self.date = date
        self.source = source
        self.success = success
        self.amount = amount
        self.ip = ip

    def validate(self):
        if self.amount is not None:
            validate_amount(self.amount)


class StatusResponse(BaseModel):
    """Status response."""

    def __init__(
        self,
        transactionId: str,
        status: str,
        currency: str,
        refno: str,
        merchantId: Optional[str] = None,
        type: Optional[str] = None,
        paymentMethod: Optional[str] = None,
        detail: Optional[StatusDetail] = None,
        card: Optional[Dict[str, Any]] = None,
        history: Optional[List[HistoryEntry]] = None,
        language: Optional[str] = None,
        mcp: Optional[Dict[str, Any]] = None,
    ):
        self.transactionId = transactionId
        self.merchantId = merchantId
        self.type = type
        self.status = status
        self.currency = currency
        self.refno = refno
        self.paymentMethod = paymentMethod
        self.detail = detail
        self.card = card
        self.history = history or []
        self.language = language
        self.mcp = mcp

    def validate(self):
        validate_length(self.currency, 3, 3, "currency")
        validate_length(self.refno, 1, 40, "refno")

        if self.history:
            for entry in self.history:
                if isinstance(entry, dict):
                    entry = HistoryEntry.from_dict(entry)
                entry.validate()


# ============== ALIAS RESPONSE MODELS ==============


class NetworkTokenInfo(BaseModel):
    """Network token information."""

    def __init__(
        self,
        expiryMonth: Optional[str] = None,
        expiryYear: Optional[str] = None,
        status: Optional[str] = None,
        paymentAccountReference: Optional[str] = None,
        tokenRequestorId: Optional[str] = None,
        token: Optional[str] = None,
        tokenCreated: Optional[bool] = None,
    ):
        self.expiryMonth = expiryMonth
        self.expiryYear = expiryYear
        self.status = status
        self.paymentAccountReference = paymentAccountReference
        self.tokenRequestorId = tokenRequestorId
        self.token = token
        self.tokenCreated = tokenCreated

    def validate(self):
        if self.expiryMonth:
            validate_expiry_month(self.expiryMonth)
        if self.expiryYear:
            validate_regex(self.expiryYear, r"^\d{2}$", "expiryYear")


class CardInfoResponse(BaseModel):
    """Card information in alias response."""

    def __init__(
        self,
        usage: Optional[str] = None,
        expiryMonth: Optional[str] = None,
        expiryYear: Optional[str] = None,
        last4: Optional[str] = None,
        bin: Optional[str] = None,
        panRemoved: Optional[bool] = None,
        cardInfo: Optional[CardInfo] = None,
        cardOnFile: Optional[Dict[str, Any]] = None,
        networkToken: Optional[NetworkTokenInfo] = None,
    ):
        self.usage = usage
        self.expiryMonth = expiryMonth
        self.expiryYear = expiryYear
        self.last4 = last4
        self.bin = bin
        self.panRemoved = panRemoved
        self.cardInfo = cardInfo
        self.cardOnFile = cardOnFile
        self.networkToken = networkToken

    def validate(self):
        if self.expiryMonth:
            validate_expiry_month(self.expiryMonth)
        if self.expiryYear:
            validate_regex(self.expiryYear, r"^\d{2}$", "expiryYear")

        if self.cardInfo:
            if isinstance(self.cardInfo, dict):
                self.cardInfo = CardInfo.from_dict(self.cardInfo)

        if self.networkToken:
            if isinstance(self.networkToken, dict):
                self.networkToken = NetworkTokenInfo.from_dict(self.networkToken)
            self.networkToken.validate()


class AliasInfoResponse(BaseModel):
    """Alias information response."""

    def __init__(
        self,
        alias: str,
        dateCreated: Union[str, datetime.datetime],
        type: str,
        fingerprint: Optional[str] = None,
        masked: Optional[str] = None,
        validUntil: Optional[Union[str, datetime.datetime]] = None,
        card: Optional[CardInfoResponse] = None,
    ):
        self.alias = alias
        self.fingerprint = fingerprint
        self.type = type
        self.masked = masked

        # Parse dates
        if isinstance(dateCreated, str):
            self.dateCreated = datetime.datetime.fromisoformat(
                dateCreated.replace("Z", "+00:00")
            )
        else:
            self.dateCreated = dateCreated

        if validUntil:
            if isinstance(validUntil, str):
                self.validUntil = datetime.datetime.fromisoformat(
                    validUntil.replace("Z", "+00:00")
                )
            else:
                self.validUntil = validUntil
        else:
            self.validUntil = None

        self.card = card

    def validate(self):
        validate_length(self.alias, 10, 100, "alias")

        if self.card:
            if isinstance(self.card, dict):
                self.card = CardInfoResponse.from_dict(self.card)
            self.card.validate()


class AliasPatchResponse(AliasInfoResponse):
    """Alias patch response."""

    pass


class AliasConvertResponse(BaseModel):
    """Alias convert response."""

    def __init__(self, alias: str):
        self.alias = alias

    def validate(self):
        validate_length(self.alias, 10, 100, "alias")


class TokenizationOverview(BaseModel):
    """Tokenization overview."""

    def __init__(self, total: int, successful: int, failed: int):
        self.total = total
        self.successful = successful
        self.failed = failed

    def validate(self):
        if self.total < 0:
            raise ValidationError("total cannot be negative")
        if self.successful < 0:
            raise ValidationError("successful cannot be negative")
        if self.failed < 0:
            raise ValidationError("failed cannot be negative")
        if self.successful + self.failed > self.total:
            raise ValidationError("successful + failed cannot exceed total")


class TokenizationResponseItem(BaseModel):
    """Tokenization response item."""

    def __init__(
        self,
        type: str,
        alias: Optional[str] = None,
        maskedCC: Optional[str] = None,
        fingerprint: Optional[str] = None,
        validUntil: Optional[Union[str, datetime.datetime]] = None,
        expiryDate: Optional[Union[str, datetime.datetime]] = None,
        networkToken: Optional[NetworkTokenInfo] = None,
        error: Optional[Dict[str, Any]] = None,
    ):
        self.type = type
        self.alias = alias
        self.maskedCC = maskedCC
        self.fingerprint = fingerprint

        # Parse dates
        if validUntil and isinstance(validUntil, str):
            self.validUntil = datetime.datetime.fromisoformat(
                validUntil.replace("Z", "+00:00")
            )
        else:
            self.validUntil = validUntil

        if expiryDate and isinstance(expiryDate, str):
            self.expiryDate = datetime.datetime.fromisoformat(
                expiryDate.replace("Z", "+00:00")
            )
        else:
            self.expiryDate = expiryDate

        self.networkToken = networkToken
        self.error = error

    def validate(self):
        if self.alias:
            validate_length(self.alias, 10, 100, "alias")

        if self.networkToken:
            if isinstance(self.networkToken, dict):
                self.networkToken = NetworkTokenInfo.from_dict(self.networkToken)
            self.networkToken.validate()


class BulkTokenizationResponse(BaseModel):
    """Bulk tokenization response."""

    def __init__(
        self,
        overview: Union[Dict[str, Any], TokenizationOverview],
        responses: List[Union[Dict[str, Any], TokenizationResponseItem]],
    ):
        self.overview = overview
        self.responses = responses

    def validate(self):
        if isinstance(self.overview, dict):
            self.overview = TokenizationOverview.from_dict(self.overview)
        self.overview.validate()

        validated_responses = []
        for response in self.responses:
            if isinstance(response, dict):
                response = TokenizationResponseItem.from_dict(response)
            response.validate()
            validated_responses.append(response)
        self.responses = validated_responses

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        result = {
            "overview": self.overview.to_dict(exclude_none)
            if isinstance(self.overview, BaseModel)
            else self.overview,
            "responses": [
                resp.to_dict(exclude_none) if isinstance(resp, BaseModel) else resp
                for resp in self.responses
            ],
        }
        return result


class DetokenizationResponseItem(BaseModel):
    """Detokenization response item."""

    def __init__(
        self,
        type: str,
        pan: Optional[str] = None,
        cvv: Optional[str] = None,
        custom: Optional[str] = None,
        validUntil: Optional[Union[str, datetime.datetime]] = None,
        error: Optional[Dict[str, Any]] = None,
    ):
        self.type = type
        self.pan = pan
        self.cvv = cvv
        self.custom = custom

        if validUntil and isinstance(validUntil, str):
            self.validUntil = datetime.datetime.fromisoformat(
                validUntil.replace("Z", "+00:00")
            )
        else:
            self.validUntil = validUntil

        self.error = error

    def validate(self):
        if self.pan:
            validate_card_number(self.pan)
        if self.cvv and not self.cvv.isdigit():
            raise ValidationError("CVV must contain only digits")


class BulkDetokenizationResponse(BaseModel):
    """Bulk detokenization response."""

    def __init__(
        self,
        overview: Union[Dict[str, Any], TokenizationOverview],
        responses: List[Union[Dict[str, Any], DetokenizationResponseItem]],
    ):
        self.overview = overview
        self.responses = responses

    def validate(self):
        if isinstance(self.overview, dict):
            self.overview = TokenizationOverview.from_dict(self.overview)
        self.overview.validate()

        validated_responses = []
        for response in self.responses:
            if isinstance(response, dict):
                response = DetokenizationResponseItem.from_dict(response)
            response.validate()
            validated_responses.append(response)
        self.responses = validated_responses

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        result = {
            "overview": self.overview.to_dict(exclude_none)
            if isinstance(self.overview, BaseModel)
            else self.overview,
            "responses": [
                resp.to_dict(exclude_none) if isinstance(resp, BaseModel) else resp
                for resp in self.responses
            ],
        }
        return result


class AliasCardArtResponse(BaseModel):
    """Alias card art response."""

    def __init__(self, mimeType: str, encodedData: str):
        self.mimeType = mimeType
        self.encodedData = encodedData


# ============== RECONCILIATION MODELS ==============


class SaleReportRequest(BaseModel):
    """Sale report request."""

    def __init__(
        self,
        date: Union[str, datetime.datetime],
        transactionId: str,
        currency: str,
        amount: int,
        type: TransactionType,
        refno: str,
    ):
        if isinstance(date, str):
            self.date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
        else:
            self.date = date
        self.transactionId = transactionId
        self.currency = currency
        self.amount = amount
        self.type = type
        self.refno = refno

    def validate(self):
        validate_amount(self.amount)
        validate_length(self.currency, 3, 3, "currency")
        validate_length(self.refno, 1, 40, "refno")


class SaleReportResponse(BaseModel):
    """Sale report response."""

    def __init__(
        self,
        transactionId: str,
        saleDate: Union[str, datetime.datetime],
        reportedDate: Union[str, datetime.datetime],
        matchResult: str,
    ):
        self.transactionId = transactionId
        if isinstance(saleDate, str):
            self.saleDate = datetime.datetime.fromisoformat(
                saleDate.replace("Z", "+00:00")
            )
        else:
            self.saleDate = saleDate
        if isinstance(reportedDate, str):
            self.reportedDate = datetime.datetime.fromisoformat(
                reportedDate.replace("Z", "+00:00")
            )
        else:
            self.reportedDate = reportedDate
        self.matchResult = matchResult


class BulkSaleRequest(BaseModel):
    """Bulk sale report request."""

    def __init__(self, sales: List[SaleReportRequest]):
        self.sales = sales

    def validate(self):
        for sale in self.sales:
            if isinstance(sale, dict):
                sale = SaleReportRequest.from_dict(sale)
            sale.validate()


class BulkSaleResponse(BaseModel):
    """Bulk sale report response."""

    def __init__(self, sales: List[SaleReportResponse]):
        self.sales = sales

    def validate(self):
        for sale in self.sales:
            if isinstance(sale, dict):
                sale = SaleReportResponse.from_dict(sale)

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        return {
            "sales": [
                sale.to_dict(exclude_none) if isinstance(sale, BaseModel) else sale
                for sale in self.sales
            ]
        }


# ============== MULTICURRENCY MODELS ==============


class RateInfo(BaseModel):
    """Currency rate information."""

    def __init__(
        self,
        currency: str,
        currencyCode: str,
        decimalPlaces: int,
        roundUnit: int,
        value: float,
    ):
        self.currency = currency
        self.currencyCode = currencyCode
        self.decimalPlaces = decimalPlaces
        self.roundUnit = roundUnit
        self.value = value

    def validate(self):
        validate_length(self.currency, 3, 3, "currency")
        validate_length(self.currencyCode, 0, 3, "currencyCode")
        if self.decimalPlaces < 0:
            raise ValidationError("decimalPlaces cannot be negative")
        if self.roundUnit < 0:
            raise ValidationError("roundUnit cannot be negative")
        if self.value <= 0:
            raise ValidationError("value must be positive")


class RatesResponse(BaseModel):
    """Rates response."""

    def __init__(
        self, requestId: str, reportDetail: Dict[str, Any], rates: List[RateInfo]
    ):
        self.requestId = requestId
        self.reportDetail = reportDetail
        self.rates = rates

    def validate(self):
        validated_rates = []
        for rate in self.rates:
            if isinstance(rate, dict):
                rate = RateInfo.from_dict(rate)
            rate.validate()
            validated_rates.append(rate)
        self.rates = validated_rates
