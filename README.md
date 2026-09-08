# WeatherPlatform — Meteorological Analytics & Incident Intelligence

A full-stack weather analytics and incident monitoring platform built with Django, PostGIS, Django REST Framework, Celery, Redis, Scikit-Learn, and React + Vite.

---

## 14-Step Roadmap Architecture

| Step | Component | Description |
|---|---|---|
| **STEP 1** | Django + Project Structure | Configured modular architecture (`config/` + `apps/` with `weather`, `incidents`, `alerts`, `ingestion`, `dashboard`), CORS, and environment management. |
| **STEP 2** | PostgreSQL + PostGIS | GeoDjango spatial engine enabled (`django.contrib.gis.db.backends.postgis`) with PostGIS Docker container. |
| **STEP 3** | Models | `WeatherStation`, `WeatherObservation` (and `WeatherReading`), `Incident` (and `IncidentReport`) with spatial points and polygons. |
| **STEP 4** | Django REST Framework | DRF viewsets, filters, pagination, OpenAPI/Swagger via `drf-spectacular`, and GeoJSON feature serializers (`rest_framework_gis`). |
| **STEP 5** | CRUD APIs | Complete REST endpoints for stations, readings, incidents, alert rules, and events under `/api/v1/`. |
| **STEP 6** | Image/File Handling | `Incident.image` field with `upload_to="incidents/%Y/%m/"`, `multipart/form-data` API support, and media serving. |
| **STEP 7** | Redis | Integrated Redis 7 cache backend (`django-redis`) and Celery message broker / result backend. |
| **STEP 8** | Celery Background Tasks | Asynchronous task execution (`apps.ingestion.tasks`, `apps.alerts.tasks`) and Celery Beat scheduler with crontab timings. |
| **STEP 9** | Weather API Ingestion | Open-Meteo REST service (`apps/ingestion/services.py`) ingesting hourly and current telemetry for stations, plus `seed_weather_data` command. |
| **STEP 10** | ML Weather Prediction | Scikit-Learn ensemble time-series regressor with lag-feature matrix and diurnal solar harmonics predicting 24-hour trends and hazard risks. |
| **STEP 11** | React + Vite Frontend | Modern TypeScript SPA with Tailwind CSS, Lucide icons, responsive layout, and reactive dashboard views. |
| **STEP 12** | Connect React → DRF | Typed API client layer (`frontend/src/api/`) consuming endpoints with Vite reverse proxy. |
| **STEP 13** | Maps + Weather Charts | Interactive Leaflet map displaying station markers and GeoJSON incident polygons; Recharts displaying telemetry and ML forecasts. |
| **STEP 14** | Dockerize Everything | Multi-container setup in `docker-compose.yml` (`db`, `redis`, `web`, `celery-worker`, `celery-beat`, `frontend`). |

---

## Quick Start (Docker Compose)

The easiest way to run the entire full-stack system is with Docker Compose:

```bash
# 1. Start all 6 container services
docker compose up -d --build

# 2. Run database migrations
docker compose exec web python manage.py migrate

# 3. Seed default stations, sample incidents, and fetch live Open-Meteo weather
docker compose exec web python manage.py seed_weather_data
```

### Accessing the Applications
- **Web Frontend**: [http://localhost:5173](http://localhost:5173)
- **Django REST API**: [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)
- **Interactive Swagger Docs**: [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- **Django Admin**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## Key API Endpoints

### Weather Telemetry & Stations
- `GET /api/v1/weather/stations/` — List all weather stations with coordinates and latest telemetry.
- `GET /api/v1/weather/stations/geojson/` — GeoJSON FeatureCollection of stations for map rendering.
- `GET /api/v1/weather/stations/{id}/history/?hours=24` — Time-series observations for a station.
- `GET /api/v1/weather/stations/{id}/predict/` — Scikit-Learn 24-hour ML forecast and hazard risks.
- `GET /api/v1/weather/readings/` — Filterable weather observations (`timestamp`, `station`).

### Incident Command
- `GET /api/v1/incidents/incidents/` — List all incidents filterable by `severity`, `status`.
- `POST /api/v1/incidents/incidents/` — Create new incident (supports `multipart/form-data` with photo file).
- `GET /api/v1/incidents/incidents/geojson/` — GeoJSON polygon features of hazard areas.

### Automated Alerts & Ingestion
- `GET /api/v1/alerts/rules/` — Configured threshold alert rules.
- `GET /api/v1/alerts/events/` — Log of triggered threshold breach events.
- `POST /api/v1/ingestion/jobs/trigger/` — Queue an immediate live ingestion run from Open-Meteo.
- `GET /api/v1/dashboard/summary/` — High-level platform metrics and 24h aggregates.

---

## Testing

```bash
# Run unit and integration tests
docker compose exec web python manage.py test apps.weather apps.incidents
```
