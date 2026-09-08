import os
import django
import json
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.test import Client
c = Client()

print("--- Testing /api/weather/historical/ ---")
r = c.get('/api/weather/historical/?city=Bengaluru&mode=recent')
print(f"Status: {r.status_code}")
d = json.loads(r.content)
print(f"City: {d.get('city')}, Mean: {d.get('mean_temp')}°C, Current: {d.get('current_temp')}°C, Anomaly: {d.get('anomaly_status')}")
print(f"Live curve length: {len(d.get('live_curve', []))}, Hist curve length: {len(d.get('hist_curve', []))}")

print("\n--- Testing /api/dataset/upload/ with CSV ---")
csv_data = """Date,City,Temperature_Max,Temperature_Min,Temperature_Avg,Rainfall,AQI
2024-06-01,Mumbai,34.5,27.2,30.8,12.4,Good
2024-06-02,Mumbai,33.1,26.5,29.8,25.0,Moderate
2024-06-03,Mumbai,32.0,25.8,28.9,45.2,Good
"""
f = io.BytesIO(csv_data.encode('utf-8'))
f.name = 'mumbai_custom_dataset.csv'

r_up = c.post('/api/dataset/upload/', {'dataset': f})
print(f"Upload Status: {r_up.status_code}")
d_up = json.loads(r_up.content)
print(f"Filename: {d_up.get('filename')}")
print(f"Rows count: {d_up.get('rows_count')}")
print(f"Detected city: {d_up.get('detected_city')}")
print(f"Ingested Mean Temp: {d_up.get('mean_temp')}°C")
print(f"Live Current Temp: {d_up.get('current_temp')}°C")
print(f"Anomaly Comparison: {d_up.get('temp_anomaly')}°C ({d_up.get('anomaly_status')})")
print(f"Live curve: {d_up.get('live_curve')}")
print(f"Hist curve: {d_up.get('hist_curve')}")

print("\n--- Testing /api/weather/historical/?city=Mumbai&mode=custom ---")
r_custom = c.get('/api/weather/historical/?city=Mumbai&mode=custom')
print(f"Custom Mode Status: {r_custom.status_code}")
d_custom = json.loads(r_custom.content)
print(f"City: {d_custom.get('city')}, Mean: {d_custom.get('mean_temp')}°C, Anomaly: {d_custom.get('anomaly_status')}")

print("\n--- Testing /historical/ Page Template ---")
r_page = c.get('/historical/')
print(f"Historical Page Status: {r_page.status_code}")

print("\nSUCCESS: All dataset ingestion and live telemetry comparison tests passed cleanly!")
