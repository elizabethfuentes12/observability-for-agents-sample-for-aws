"""get_weather Lambda tool — daily forecast via Open-Meteo (no auth required).

Event shape (AgentCore Gateway → Lambda):
    {"city": "Miami", "target_date": "2026-08-01"}
"""

import json
import urllib.error
import urllib.parse
import urllib.request

OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _http_get(url: str, params: dict, timeout: int = 15) -> dict:
    qs = urllib.parse.urlencode(params)
    full = f"{url}?{qs}"
    parsed = urllib.parse.urlparse(full)
    if parsed.scheme not in ("https", "http"):
        raise ValueError(f"Unexpected URL scheme: {parsed.scheme!r}")
    with urllib.request.urlopen(full, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _resolve_city(city: str) -> dict | None:
    data = _http_get(OPEN_METEO_GEOCODING_URL,
                     {"name": city, "count": 1, "format": "json"})
    results = data.get("results", [])
    return results[0] if results else None


def handler(event, context):
    city = event.get("city")
    target_date = event.get("target_date")
    if not (city and target_date):
        return {"statusCode": 400,
                "body": json.dumps({"error": "missing required fields",
                                    "required": ["city", "target_date"]})}

    location = _resolve_city(city)
    if not location:
        return {"statusCode": 200,
                "body": json.dumps({"error": "city_not_found", "city": city})}

    try:
        data = _http_get(OPEN_METEO_FORECAST_URL, {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "daily": "temperature_2m_max,temperature_2m_min",
            "start_date": target_date,
            "end_date": target_date,
            "timezone": "auto",
        })
    except urllib.error.HTTPError as e:
        return {"statusCode": 200,
                "body": json.dumps({"error": "forecast_unavailable", "status_code": e.code,
                                    "city": city, "target_date": target_date})}

    daily = data.get("daily", {})
    if not daily.get("time"):
        return {"statusCode": 200,
                "body": json.dumps({"error": "no_forecast_for_date", "city": city})}

    return {"statusCode": 200,
            "body": json.dumps({"city": location["name"],
                                "temperature_max_c": daily["temperature_2m_max"][0],
                                "temperature_min_c": daily["temperature_2m_min"][0]})}
