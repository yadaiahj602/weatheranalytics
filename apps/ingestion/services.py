"""Services for external weather data ingestion via Open-Meteo."""
import logging
from datetime import datetime, timezone
import requests
from django.contrib.gis.geos import Point, Polygon
from django.utils.dateparse import parse_datetime

from apps.weather.models import WeatherObservation, WeatherStation

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

DEFAULT_STATIONS = [
    {"code": "JFK", "name": "New York John F. Kennedy", "lat": 40.6413, "lon": -73.7781, "elevation_m": 4.0},
    {"code": "LHR", "name": "London Heathrow", "lat": 51.4700, "lon": -0.4543, "elevation_m": 25.0},
    {"code": "HND", "name": "Tokyo Haneda", "lat": 35.5494, "lon": 139.7798, "elevation_m": 11.0},
    {"code": "CDG", "name": "Paris Charles de Gaulle", "lat": 49.0097, "lon": 2.5479, "elevation_m": 119.0},
    {"code": "SYD", "name": "Sydney Kingsford Smith", "lat": -33.9399, "lon": 151.1753, "elevation_m": 6.0},
    {"code": "BOM", "name": "Mumbai Chhatrapati Shivaji", "lat": 19.0896, "lon": 72.8656, "elevation_m": 14.0},
    {"code": "SFO", "name": "San Francisco International", "lat": 37.6213, "lon": -122.3790, "elevation_m": 4.0},
    {"code": "ORD", "name": "Chicago O'Hare", "lat": 41.9742, "lon": -87.9073, "elevation_m": 204.0},
    {"code": "SIN", "name": "Singapore Changi", "lat": 1.3644, "lon": 103.9915, "elevation_m": 7.0},
    {"code": "BER", "name": "Berlin Brandenburg", "lat": 52.3667, "lon": 13.5033, "elevation_m": 48.0},
]


def seed_default_stations() -> list[WeatherStation]:
    """Create default world weather stations if they do not exist."""
    stations = []
    for s in DEFAULT_STATIONS:
        station, created = WeatherStation.objects.get_or_create(
            code=s["code"],
            defaults={
                "name": s["name"],
                "location": Point(s["lon"], s["lat"], srid=4326),
                "elevation_m": s["elevation_m"],
                "is_active": True,
            },
        )
        if created:
            logger.info("Created default weather station: %s", station)
        stations.append(station)
    return stations


def seed_sample_incidents():
    """Create sample weather incidents with polygons for testing and map display."""
    from apps.incidents.models import Incident
    from django.utils import timezone as dj_timezone

    if Incident.objects.exists():
        return

    now = dj_timezone.now()
    sample_data = [
        {
            "title": "Severe Coastal Flash Flood Warning",
            "description": "Rapid inundation along low-lying tidal corridors following prolonged heavy rainfall.",
            "incident_type": Incident.IncidentType.FLOOD,
            "severity": Incident.Severity.CRITICAL,
            "status": Incident.Status.OPEN,
            "polygon": Polygon([
                (-74.1, 40.5),
                (-73.8, 40.5),
                (-73.8, 40.8),
                (-74.1, 40.8),
                (-74.1, 40.5),
            ], srid=4326),
            "start_time": now - dj_timezone.timedelta(hours=6),
        },
        {
            "title": "Metropolitan Severe Heatwave Advisory",
            "description": "Sustained daytime temperatures exceeding 38°C with high humidity index.",
            "incident_type": Incident.IncidentType.HEATWAVE,
            "severity": Incident.Severity.HIGH,
            "status": Incident.Status.MONITORING,
            "polygon": Polygon([
                (72.7, 18.9),
                (73.1, 18.9),
                (73.1, 19.3),
                (72.7, 19.3),
                (72.7, 18.9),
            ], srid=4326),
            "start_time": now - dj_timezone.timedelta(hours=12),
        },
        {
            "title": "Gale-Force Wind and Squall Front",
            "description": "Gusts reaching up to 45 knots affecting maritime and suburban infrastructure.",
            "incident_type": Incident.IncidentType.STORM,
            "severity": Incident.Severity.MEDIUM,
            "status": Incident.Status.OPEN,
            "polygon": Polygon([
                (-0.6, 51.3),
                (-0.2, 51.3),
                (-0.2, 51.6),
                (-0.6, 51.6),
                (-0.6, 51.3),
            ], srid=4326),
            "start_time": now - dj_timezone.timedelta(hours=3),
        },
    ]

    for item in sample_data:
        Incident.objects.create(
            title=item["title"],
            description=item["description"],
            incident_type=item["incident_type"],
            severity=item["severity"],
            status=item["status"],
            affected_area=item["polygon"],
            start_time=item["start_time"],
        )
    logger.info("Created sample incidents with polygons for testing.")


def fetch_station_weather(station: WeatherStation) -> int:
    """Fetch recent observation history and current conditions from Open-Meteo for a station."""
    if not station.location:
        return 0

    lat = station.location.y
    lon = station.location.x

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "precipitation",
            "cloud_cover",
        ],
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "precipitation",
            "cloud_cover",
        ],
        "past_days": 2,
        "forecast_days": 1,
        "timezone": "UTC",
    }

    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=12)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        logger.warning("Open-Meteo request failed for station %s: %s", station.code, exc)
        return 0

    records_count = 0

    # 1. Process current observation
    current = data.get("current")
    if current and "time" in current:
        dt = parse_datetime(current["time"])
        if dt:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            WeatherObservation.objects.update_or_create(
                station=station,
                timestamp=dt,
                defaults={
                    "temperature_c": current.get("temperature_2m"),
                    "humidity_pct": current.get("relative_humidity_2m"),
                    "pressure_hpa": current.get("surface_pressure"),
                    "wind_speed_ms": current.get("wind_speed_10m"),
                    "wind_direction_deg": current.get("wind_direction_10m"),
                    "precipitation_mm": current.get("precipitation"),
                    "cloud_cover_pct": current.get("cloud_cover"),
                    "raw_data": current,
                },
            )
            records_count += 1

    # 2. Process hourly time-series observations
    hourly = data.get("hourly")
    if hourly and "time" in hourly:
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        humids = hourly.get("relative_humidity_2m", [])
        pressures = hourly.get("surface_pressure", [])
        wind_speeds = hourly.get("wind_speed_10m", [])
        wind_dirs = hourly.get("wind_direction_10m", [])
        precips = hourly.get("precipitation", [])
        clouds = hourly.get("cloud_cover", [])

        observations_to_create = []
        for i, t_str in enumerate(times):
            dt = parse_datetime(t_str)
            if not dt:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            # Skip future timestamps for historical observation table
            if dt > datetime.now(tz=timezone.utc):
                continue

            obs, created = WeatherObservation.objects.update_or_create(
                station=station,
                timestamp=dt,
                defaults={
                    "temperature_c": temps[i] if i < len(temps) else None,
                    "humidity_pct": humids[i] if i < len(humids) else None,
                    "pressure_hpa": pressures[i] if i < len(pressures) else None,
                    "wind_speed_ms": wind_speeds[i] if i < len(wind_speeds) else None,
                    "wind_direction_deg": wind_dirs[i] if i < len(wind_dirs) else None,
                    "precipitation_mm": precips[i] if i < len(precips) else None,
                    "cloud_cover_pct": clouds[i] if i < len(clouds) else None,
                },
            )
            if created:
                records_count += 1

    return records_count


def ingest_all_active_stations() -> dict:
    """Ingest weather data for all active weather stations."""
    seed_default_stations()
    seed_sample_incidents()

    stations = WeatherStation.objects.filter(is_active=True)
    total_records = 0
    station_results = {}

    for station in stations:
        count = fetch_station_weather(station)
        total_records += count
        station_results[station.code] = count

    # Trigger alert rules evaluation
    try:
        from apps.alerts.tasks import evaluate_alert_rules
        evaluate_alert_rules()
    except Exception as e:
        logger.warning("Could not evaluate alert rules: %s", e)

    return {
        "stations_polled": stations.count(),
        "total_records_processed": total_records,
        "by_station": station_results,
    }
