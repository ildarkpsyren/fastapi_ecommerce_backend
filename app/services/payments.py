"""Placeholder payment service module."""
from app.models.order import Order


def process_payment_placeholder(order: Order) -> None:
    """Placeholder for integrating with a payment gateway.

    The function intentionally does nothing other than documenting where payment
    integration should be plugged in once a provider is selected.
    """

    # Payment integration will be implemented here in the future.
    return None
