import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()
from django.test import Client
c = Client()

# Test page templates (no Open-Meteo calls, just template rendering)
pages = ['/', '/cities/', '/forecast/', '/prediction/', '/alerts/', '/assistant/']
print('=== Page Template Routes ===')
for path in pages:
    r = c.get(path)
    mark = 'OK ' if r.status_code == 200 else 'ERR'
    print(f'  {mark} [{r.status_code}] GET {path}')

print()
print('=== API Routes (no Open-Meteo) ===')

r = c.get('/api/incidents/list/')
print(f'  {"OK " if r.status_code==200 else "ERR"} [{r.status_code}] GET /api/incidents/list/')

r = c.get('/api/alerts/')
print(f'  {"OK " if r.status_code==200 else "ERR"} [{r.status_code}] GET /api/alerts/')

r = c.get('/api/ai/chat/?q=flood+risk+in+Bengaluru')
print(f'  {"OK " if r.status_code==200 else "ERR"} [{r.status_code}] GET /api/ai/chat/')

r = c.post(
    '/api/incidents/report/',
    data=json.dumps({'description': 'waterlogging near roads', 'lat': 12.97, 'lon': 77.59}),
    content_type='application/json'
)
d = json.loads(r.content)
print(f'  {"OK " if r.status_code==200 else "ERR"} [{r.status_code}] POST /api/incidents/report/ -> category={d.get("category")} precautions_count={len(d.get("precautions",[]))}')

r2 = c.post(
    '/api/ai/chat/',
    data=json.dumps({'query': 'What should I do during a heatwave?'}),
    content_type='application/json'
)
d2 = json.loads(r2.content)
reply_preview = str(d2.get('reply', ''))[:70]
print(f'  {"OK " if r2.status_code==200 else "ERR"} [{r2.status_code}] POST /api/ai/chat/ -> {reply_preview}...')

print()
print('=== All checks complete ===')
