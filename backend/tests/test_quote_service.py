from app.services.quote_service import (
    calculate_fulfillment_status,
)


def test_available_fulfillment():
    result = calculate_fulfillment_status(
        requested=30,
        available=105,
    )

    assert result == "available"


def test_partial_fulfillment():
    result = calculate_fulfillment_status(
        requested=150,
        available=105,
    )

    assert result == "partial"


def test_unavailable_fulfillment():
    result = calculate_fulfillment_status(
        requested=10,
        available=0,
    )

    assert result == "unavailable"