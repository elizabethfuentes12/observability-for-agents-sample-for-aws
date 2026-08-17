"""Travel agent runtime — deployed to Amazon Bedrock AgentCore Runtime.

Runtime-only architecture: the three tools live inside the agent (same pattern as
demos 01-03), no Gateway. `search_flights` calls the Duffel sandbox, `get_weather`
calls Open-Meteo, and `book_flight` writes to the FlightBookings DynamoDB table.

The AgentCore entrypoint contract: import BedrockAgentCoreApp, create the app, and
decorate the request handler with @app.entrypoint.
"""

import json
import os
from typing import Optional

import boto3
import requests
import urllib.parse

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

app = BedrockAgentCoreApp()

MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
FLIGHT_BOOKINGS_TABLE = os.environ.get("FLIGHT_BOOKINGS_TABLE", "FlightBookings")

DUFFEL_API_BASE_URL = "https://api.duffel.com"
DUFFEL_API_VERSION = "v2"
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

_dynamodb = boto3.resource("dynamodb")
_bookings_table = _dynamodb.Table(FLIGHT_BOOKINGS_TABLE)

# Offers returned by a prior search_flights call, so a booking can only reference an
# offer the agent actually saw.
_SEEN_OFFERS: dict[str, dict] = {}


def _duffel_headers() -> dict:
    api_key = os.environ.get("DUFFEL_API_KEY")
    if not api_key:
        raise RuntimeError("DUFFEL_API_KEY is not set on the runtime environment.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Duffel-Version": DUFFEL_API_VERSION,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


@tool
def search_flights(origin: str, destination: str, departure_date: str) -> dict:
    """Search one-way flight offers (Duffel sandbox). Present these to the traveler to choose from.

    Args:
        origin: Origin airport IATA code (3 letters, e.g. "JFK").
        destination: Destination airport IATA code (3 letters, e.g. "MIA").
        departure_date: Departure date in YYYY-MM-DD format.

    Returns:
        A dict with `offers`: up to 5 options, each with `offer_id`, `airline`,
        `total_amount`, `currency`, `departing_at`, `arriving_at`.
    """
    payload = {
        "data": {
            "slices": [{"origin": origin.upper(), "destination": destination.upper(),
                        "departure_date": departure_date}],
            "passengers": [{"type": "adult"}],
            "cabin_class": "economy",
        }
    }
    try:
        resp = requests.post(
            f"{DUFFEL_API_BASE_URL}/air/offer_requests", headers=_duffel_headers(),
            params={"return_offers": "true"}, json=payload, timeout=40,
        )
        resp.raise_for_status()
    except requests.HTTPError as exc:
        return {"error": "search_failed", "status_code": exc.response.status_code}
    data = resp.json().get("data", {})
    offers = sorted(data.get("offers", []), key=lambda o: float(o.get("total_amount", 1e9)))[:5]
    results = []
    for o in offers:
        seg = o.get("slices", [{}])[0].get("segments", [{}])[0]
        offer = {
            "offer_id": o.get("id"),
            "airline": o.get("owner", {}).get("name"),
            "total_amount": o.get("total_amount"),
            "currency": o.get("total_currency"),
            "departing_at": seg.get("departing_at"),
            "arriving_at": seg.get("arriving_at"),
        }
        _SEEN_OFFERS[o["id"]] = offer
        results.append(offer)
    return {"origin": origin.upper(), "destination": destination.upper(), "offers": results}


def _resolve_city(city: str) -> Optional[dict]:
    resp = requests.get(OPEN_METEO_GEOCODING_URL,
                        params={"name": city, "count": 1, "format": "json"}, timeout=15)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0] if results else None


@tool
def get_weather(city: str, target_date: str) -> dict:
    """Get the daily weather forecast for a city on a date (Open-Meteo), to advise on packing.

    Args:
        city: City name, e.g. "Miami".
        target_date: Date in YYYY-MM-DD format, within the next ~16 days.

    Returns:
        A dict with `city`, `temperature_max_c`, `temperature_min_c`, or an `error`.
    """
    location = _resolve_city(city)
    if not location:
        return {"error": "city_not_found", "city": city}
    resp = requests.get(OPEN_METEO_FORECAST_URL,
                        params={"latitude": location["latitude"], "longitude": location["longitude"],
                                "daily": "temperature_2m_max,temperature_2m_min",
                                "start_date": target_date, "end_date": target_date, "timezone": "auto"},
                        timeout=15)
    resp.raise_for_status()
    daily = resp.json().get("daily", {})
    if not daily.get("time"):
        return {"error": "no_forecast_for_date", "city": city}
    return {"city": location["name"], "temperature_max_c": daily["temperature_2m_max"][0],
            "temperature_min_c": daily["temperature_2m_min"][0]}


@tool
def book_flight(offer_id: str, given_name: str, family_name: str,
                amount: str, currency: str = "USD") -> dict:
    """Book a chosen flight offer for a named passenger into our booking system.

    Call this only after `search_flights` and once the traveler has chosen an offer.
    Records the booking in the FlightBookings DynamoDB table.

    Args:
        offer_id: The `offer_id` of the chosen flight (from `search_flights`).
        given_name: Passenger's first name.
        family_name: Passenger's last name.
        amount: The offer's `total_amount` (from the chosen offer).
        currency: The offer's `currency` (default "USD").

    Returns:
        A dict with `status`, `booking_reference`, and `passenger` on success.
    """
    if offer_id not in _SEEN_OFFERS:
        return {"error": "unknown_offer",
                "message": "Search for flights first; that offer_id was not seen in a search."}
    booking_ref = f"BK-{offer_id[-6:].upper()}"
    _bookings_table.put_item(Item={
        "booking_reference": booking_ref,
        "offer_id": offer_id,
        "passenger": f"{given_name} {family_name}",
        "amount": str(amount),
        "currency": currency,
    })
    return {"status": "confirmed", "booking_reference": booking_ref,
            "passenger": f"{given_name} {family_name}", "amount": str(amount),
            "currency": currency}


SYSTEM_PROMPT = (
    "You are a travel assistant. Search flights, check the weather at the destination, "
    "and book the best option for the traveler without asking for confirmation. Be concise."
)

_model = BedrockModel(model_id=MODEL_ID)
_agent = Agent(model=_model, system_prompt=SYSTEM_PROMPT,
               tools=[search_flights, get_weather, book_flight])


@app.entrypoint
def invoke(payload: dict) -> str:
    """AgentCore Runtime entrypoint: JSON payload in, agent text response out."""
    prompt = payload.get("prompt", "")
    if not prompt:
        return "Please provide a 'prompt' field in the request payload."
    result = _agent(prompt)
    return result.message["content"][0]["text"]


if __name__ == "__main__":
    app.run()
