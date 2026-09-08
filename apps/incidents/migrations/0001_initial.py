import django.contrib.gis.db.models.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Incident',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('incident_type', models.CharField(choices=[('flood', 'Flood'), ('storm', 'Storm'), ('heatwave', 'Heatwave'), ('drought', 'Drought'), ('tornado', 'Tornado'), ('blizzard', 'Blizzard'), ('other', 'Other')], default='other', max_length=20)),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=10)),
                ('status', models.CharField(choices=[('open', 'Open'), ('monitoring', 'Monitoring'), ('resolved', 'Resolved'), ('closed', 'Closed')], default='open', max_length=20)),
                ('affected_area', django.contrib.gis.db.models.fields.PolygonField(blank=True, help_text='WGS84 polygon of the affected region.', null=True, srid=4326)),
                ('image', models.ImageField(blank=True, help_text='Photo or attachment of the incident.', null=True, upload_to='incidents/%Y/%m/')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reported_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reported_incidents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Incident',
                'verbose_name_plural': 'Incidents',
                'ordering': ['-start_time'],
            },
        ),
        migrations.AddIndex(
            model_name='incident',
            index=models.Index(fields=['status', 'severity'], name='incidents_i_status_6ebcf9_idx'),
        ),
        migrations.AddIndex(
            model_name='incident',
            index=models.Index(fields=['incident_type'], name='incidents_i_inciden_f6ff8b_idx'),
        ),
        migrations.AddIndex(
            model_name='incident',
            index=models.Index(fields=['start_time'], name='incidents_i_start_t_be44e2_idx'),
        ),
        migrations.CreateModel(
            name='IncidentReport',
            fields=[],
            options={
                'verbose_name': 'Incident Report',
                'verbose_name_plural': 'Incident Reports',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('incidents.incident',),
        ),
    ]
