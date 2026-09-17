from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
SOILGRIDS_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"


class ExternalDataError(Exception):
    """Raised when an external data provider cannot be reached or parsed."""


def _get_json(
    url: str,
    params: dict,
    timeout: int = 10,
) -> dict:
    query_string = urlencode(params, doseq=True)
    request_url = f"{url}?{query_string}"

    request = Request(
        request_url,
        headers={
            "User-Agent": "AgriTwin-AI/1.0",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            status_code = response.status
            body = response.read().decode("utf-8")

        if status_code < 200 or status_code >= 300:
            raise ExternalDataError(
                f"External service returned HTTP {status_code}"
            )

        return json.loads(body)

    except HTTPError as exc:
        raise ExternalDataError(
            f"External service returned HTTP {exc.code}"
        ) from exc

    except URLError as exc:
        raise ExternalDataError(
            "External service could not be reached"
        ) from exc

    except TimeoutError as exc:
        raise ExternalDataError(
            "External service request timed out"
        ) from exc

    except json.JSONDecodeError as exc:
        raise ExternalDataError(
            "External service returned invalid JSON"
        ) from exc


def get_live_weather(
    latitude: float,
    longitude: float,
) -> dict:
    """
    Fetch current + 7-day weather data from Open-Meteo.
    No API key is required for the public endpoint.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "rain,"
            "wind_speed_10m,"
            "weather_code"
        ),
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "et0_fao_evapotranspiration"
        ),
        "forecast_days": 7,
        "timezone": "auto",
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }

    data = _get_json(
        OPEN_METEO_FORECAST_URL,
        params,
    )

    return {
        "provider": "Open-Meteo",
        "latitude": latitude,
        "longitude": longitude,
        "timezone": data.get("timezone"),
        "current": data.get("current", {}),
        "daily": data.get("daily", {}),
    }


def get_soil_data(
    latitude: float,
    longitude: float,
) -> dict:
    """
    Fetch point-based soil information from SoilGrids.

    The API may be temporarily unavailable. We deliberately
    propagate a clear provider error rather than inventing values.
    """

    params = {
        "lon": longitude,
        "lat": latitude,
        "property": [
            "phh2o",
            "nitrogen",
            "soc",
            "clay",
        ],
        "depth": [
            "0-5cm",
            "5-15cm",
        ],
        "value": "mean",
    }

    data = _get_json(
        SOILGRIDS_URL,
        params,
        timeout=15,
    )

    return {
        "provider": "SoilGrids",
        "latitude": latitude,
        "longitude": longitude,
        "properties": data.get("properties", {}),
    }