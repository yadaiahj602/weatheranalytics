import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='WeatherStation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Station identifier code (e.g. IATA or WMO code).', max_length=20, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text='WGS84 point geometry (longitude, latitude).', srid=4326)),
                ('elevation_m', models.FloatField(blank=True, help_text='Elevation above sea level in metres.', null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Weather Station',
                'verbose_name_plural': 'Weather Stations',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='WeatherObservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(db_index=True, help_text='UTC timestamp of the observation.')),
                ('temperature_c', models.FloatField(blank=True, help_text='Air temperature (°C).', null=True)),
                ('humidity_pct', models.FloatField(blank=True, help_text='Relative humidity (%).', null=True)),
                ('pressure_hpa', models.FloatField(blank=True, help_text='Sea-level pressure (hPa).', null=True)),
                ('wind_speed_ms', models.FloatField(blank=True, help_text='Wind speed (m/s).', null=True)),
                ('wind_direction_deg', models.FloatField(blank=True, help_text='Wind direction in degrees from true north (0–360).', null=True)),
                ('precipitation_mm', models.FloatField(blank=True, help_text='Precipitation accumulation (mm).', null=True)),
                ('cloud_cover_pct', models.FloatField(blank=True, help_text='Cloud cover (%).', null=True)),
                ('visibility_m', models.FloatField(blank=True, help_text='Visibility (metres).', null=True)),
                ('raw_data', models.JSONField(blank=True, help_text='Original JSON payload from the source API for auditing.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='observations', to='weather.weatherstation')),
            ],
            options={
                'verbose_name': 'Weather Observation',
                'verbose_name_plural': 'Weather Observations',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='weatherstation',
            index=models.Index(fields=['code'], name='weather_wea_code_4b9a11_idx'),
        ),
        migrations.AddIndex(
            model_name='weatherstation',
            index=models.Index(fields=['is_active'], name='weather_wea_is_acti_06ffb7_idx'),
        ),
        migrations.AddIndex(
            model_name='weatherobservation',
            index=models.Index(fields=['station', 'timestamp'], name='weather_wea_station_d883f3_idx'),
        ),
        migrations.AddIndex(
            model_name='weatherobservation',
            index=models.Index(fields=['timestamp'], name='weather_wea_timesta_1215fc_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='weatherobservation',
            unique_together={('station', 'timestamp')},
        ),
        migrations.CreateModel(
            name='WeatherReading',
            fields=[],
            options={
                'verbose_name': 'Weather Reading',
                'verbose_name_plural': 'Weather Readings',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('weather.weatherobservation',),
        ),
    ]
