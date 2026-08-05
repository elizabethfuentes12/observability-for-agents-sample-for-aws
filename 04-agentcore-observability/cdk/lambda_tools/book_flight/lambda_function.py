"""book_flight Lambda tool — writes a confirmed booking to the FlightBookings DynamoDB table.

The DynamoDB table name is read from the FLIGHT_BOOKINGS_TABLE environment variable, set
by CDK to the CDK-generated table name. Primary key: `booking_reference` (string).

Event shape (AgentCore Gateway → Lambda):
    {"offer_id": "off_...", "given_name": "John", "family_name": "Doe",
     "amount": "89.54", "currency": "USD"}
"""

import json
import os

import boto3

FLIGHT_BOOKINGS_TABLE = os.environ.get("FLIGHT_BOOKINGS_TABLE", "FlightBookings")
_dynamodb = boto3.resource("dynamodb")
_table = _dynamodb.Table(FLIGHT_BOOKINGS_TABLE)


def _booking_reference(offer_id: str) -> str:
    """Deterministic booking reference derived from the offer_id last 6 characters."""
    return f"BK-{offer_id[-6:].upper()}"


def handler(event, context):
    offer_id = event.get("offer_id")
    given_name = event.get("given_name")
    family_name = event.get("family_name")
    amount = event.get("amount")
    currency = event.get("currency", "USD")

    if not (offer_id and given_name and family_name and amount):
        return {"statusCode": 400,
                "body": json.dumps({"error": "missing required fields",
                                    "required": ["offer_id", "given_name", "family_name", "amount"]})}

    booking_ref = _booking_reference(offer_id)
    _table.put_item(Item={
        "booking_reference": booking_ref,
        "offer_id": offer_id,
        "passenger": f"{given_name} {family_name}",
        "amount": str(amount),
        "currency": currency,
    })

    return {"statusCode": 200,
            "body": json.dumps({"status": "confirmed",
                                "booking_reference": booking_ref,
                                "passenger": f"{given_name} {family_name}",
                                "amount": str(amount),
                                "currency": currency})}
