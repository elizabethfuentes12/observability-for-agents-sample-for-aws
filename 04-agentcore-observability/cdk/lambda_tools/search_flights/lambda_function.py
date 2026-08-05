"""search_flights Lambda tool — queries the Duffel sandbox API for one-way flight offers.

Reads the Duffel API key from the DUFFEL_API_KEY environment variable (set by CDK from
Secrets Manager or as a plain env var during deployment). Returns up to 5 offers sorted
by price.

Event shape (AgentCore Gateway → Lambda):
    {"origin": "JFK", "destination": "MIA", "departure_date": "2026-08-01"}
"""

import json
import os

import urllib.request
import urllib.error

DUFFEL_API_BASE_URL = "https://api.duffel.com"
DUFFEL_API_VERSION = "v2"


def _duffel_headers() -> dict:
    api_key = os.environ.get("DUFFEL_API_KEY")
    if not api_key:
        raise RuntimeError(
            "DUFFEL_API_KEY is not set. Create a free sandbox token at https://app.duffel.com "
            "(More -> Developers -> Access tokens) and set it as an environment variable on the Lambda."
        )
    return {
        "Authorization": f"Bearer {api_key}",
        "Duffel-Version": DUFFEL_API_VERSION,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _search_offers(origin: str, destination: str, departure_date: str) -> dict:
    payload = {
        "data": {
            "slices": [{"origin": origin.upper(), "destination": destination.upper(),
                        "departure_date": departure_date}],
            "passengers": [{"type": "adult"}],
            "cabin_class": "economy",
        }
    }
    url = f"{DUFFEL_API_BASE_URL}/air/offer_requests?return_offers=true"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=_duffel_headers(),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": "search_failed", "status_code": e.code}

    data = body.get("data", {})
    offers = sorted(data.get("offers", []),
                    key=lambda o: float(o.get("total_amount", 1e9)))[:5]
    results = []
    for o in offers:
        seg = o.get("slices", [{}])[0].get("segments", [{}])[0]
        results.append({
            "offer_id": o.get("id"),
            "airline": o.get("owner", {}).get("name"),
            "total_amount": o.get("total_amount"),
            "currency": o.get("total_currency"),
            "departing_at": seg.get("departing_at"),
            "arriving_at": seg.get("arriving_at"),
        })
    return {"origin": origin.upper(), "destination": destination.upper(), "offers": results}


def handler(event, context):
    origin = event.get("origin")
    destination = event.get("destination")
    departure_date = event.get("departure_date")
    if not (origin and destination and departure_date):
        return {"statusCode": 400,
                "body": json.dumps({"error": "missing required fields",
                                    "required": ["origin", "destination", "departure_date"]})}

    result = _search_offers(origin, destination, departure_date)
    return {"statusCode": 200, "body": json.dumps(result)}
