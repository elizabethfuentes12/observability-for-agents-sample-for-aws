"""A travel-booking agent's tools: real flight search, real weather, a local booking ledger.

This is the agent every demo in this series instruments — it does its normal job (search
flights, check weather, book) against REAL APIs. No injected failures, no chaos effects: the
point of this series is to make the agent's *normal* behavior visible (reasoning steps,
tool-call cascades, token cost per cycle), not to break it on purpose.

- `search_flights` -> Duffel sandbox API (real one-way offers). Needs DUFFEL_API_KEY.
- `book_flight`     -> writes to a local SQLite ledger (no paid order is ever placed).
- `get_weather`     -> Open-Meteo (no auth, real daily forecast).

Adapted, with thanks, from Ricardo Ceci's open course
"curso-strands-agentcore-2026" (clase-1 / clase-4 travel agent):
https://github.com/ricardoceci/curso-strands-agentcore-2026
"""

import os
import sqlite3
from typing import Optional

import requests
from strands import tool

DUFFEL_API_BASE_URL = "https://api.duffel.com"
DUFFEL_API_VERSION = "v2"

# Offers returned by a prior search_flights call, so a booking can only reference an offer the
# agent actually saw (not a hallucinated offer_id).
_SEEN_OFFERS: dict[str, dict] = {}


def _duffel_headers() -> dict:
    api_key = os.environ.get("DUFFEL_API_KEY")
    if not api_key:
        raise RuntimeError(
            "DUFFEL_API_KEY is not set. Create a free sandbox token at "
            "https://app.duffel.com (More -> Developers -> Access tokens) and add "
            "it to your .env file as DUFFEL_API_KEY=duffel_test_..."
        )
    return {
        "Authorization": f"Bearer {api_key}",
        "Duffel-Version": DUFFEL_API_VERSION,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


# --- The local booking ledger (a SQLite file you can query) -------------------

DB_PATH = os.path.join(os.path.dirname(__file__), "bookings.db")


def init_booking_db() -> None:
    """Create a fresh local booking ledger. Call once at the start of each run."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "CREATE TABLE bookings ("
        "  booking_reference TEXT PRIMARY KEY,"
        "  offer_id TEXT,"
        "  passenger TEXT,"
        "  amount TEXT,"
        "  currency TEXT"
        ")"
    )
    con.commit()
    con.close()


def query_booked_offers() -> list[dict]:
    """Read the ledger directly for what is booked, independent of anything the agent claims."""
    if not os.path.exists(DB_PATH):
        return []
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT booking_reference, offer_id, passenger, amount, currency FROM bookings")]
    con.close()
    return rows


def _persist_booking(offer_id: str, given_name: str, family_name: str,
                     amount: str, currency: str) -> str:
    """Write a confirmation to the ledger and return the booking reference."""
    booking_ref = f"BK-{offer_id[-6:].upper()}"
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT OR REPLACE INTO bookings "
        "(booking_reference, offer_id, passenger, amount, currency) VALUES (?, ?, ?, ?, ?)",
        (booking_ref, offer_id, f"{given_name} {family_name}", amount, currency),
    )
    con.commit()
    con.close()
    return booking_ref


# --- Tools --------------------------------------------------------------------

@tool
def search_flights(origin: str, destination: str, departure_date: str) -> dict:
    """Search one-way flight offers (Duffel sandbox). Present these to the traveler to choose from.

    Args:
        origin: Origin airport IATA code (3 letters, e.g. "JFK").
        destination: Destination airport IATA code (3 letters, e.g. "MIA").
        departure_date: Departure date in YYYY-MM-DD format.

    Returns:
        A dict with `offers`: up to 5 options, each with `offer_id`, `airline`,
        `total_amount`, `currency`, `departing_at`, `arriving_at`. Pass the chosen
        offer's `offer_id` to `book_flight`.
    """
    payload = {
        "data": {
            "slices": [{"origin": origin.upper(), "destination": destination.upper(),
                        "departure_date": departure_date}],
            "passengers": [{"type": "adult"}],
            "cabin_class": "economy",
        }
    }
    resp = requests.post(
        f"{DUFFEL_API_BASE_URL}/air/offer_requests", headers=_duffel_headers(),
        params={"return_offers": "true"}, json=payload, timeout=40,
    )
    if resp.status_code >= 400:
        return {"error": "search_failed", "status_code": resp.status_code}
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
        _SEEN_OFFERS[o["id"]] = offer   # remember it so a booking can validate the choice
        results.append(offer)
    return {"origin": origin.upper(), "destination": destination.upper(), "offers": results}


@tool
def book_flight(offer_id: str, given_name: str, family_name: str,
                amount: str, currency: str = "USD") -> dict:
    """Book a chosen flight offer for a named passenger into our booking system.

    Call this only after `search_flights` and once the traveler has chosen an offer.
    Records the booking in the local ledger (it does not place a paid order with the airline).

    Args:
        offer_id: The `offer_id` of the chosen flight (from `search_flights`).
        given_name: Passenger's first name.
        family_name: Passenger's last name.
        amount: The offer's `total_amount` (from the chosen offer).
        currency: The offer's `currency` (default "USD").

    Returns:
        A dict with `status`, our `booking_reference`, and the `passenger` on
        success; an `error` if the offer wasn't from a prior search.
    """
    if offer_id not in _SEEN_OFFERS:
        return {"error": "unknown_offer",
                "message": "Search for flights first; that offer_id was not seen in a search."}
    booking_ref = _persist_booking(offer_id, given_name, family_name, amount, currency)
    return {"status": "confirmed", "booking_reference": booking_ref,
            "passenger": f"{given_name} {family_name}", "amount": amount, "currency": currency}


@tool
def list_my_bookings() -> dict:
    """List the bookings currently in the ledger, to verify what is confirmed."""
    rows = query_booked_offers()
    return {"bookings": rows, "count": len(rows)}


# --- Weather (Open-Meteo, no auth) ---------------------------------------------

OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


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
