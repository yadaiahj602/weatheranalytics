from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('weather', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True, default='')),
                ('condition_type', models.CharField(choices=[('temp_above', 'Temperature Above'), ('temp_below', 'Temperature Below'), ('wind_above', 'Wind Speed Above'), ('precip_above', 'Precipitation Above'), ('humidity_above', 'Humidity Above'), ('humidity_below', 'Humidity Below'), ('pressure_below', 'Pressure Below')], max_length=20)),
                ('threshold', models.FloatField(help_text='Numeric threshold value that triggers this rule.')),
                ('channel', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS'), ('webhook', 'Webhook'), ('slack', 'Slack')], default='email', max_length=20)),
                ('recipients', models.JSONField(default=list, help_text='List of recipient addresses/URLs for the chosen channel.')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('station', models.ForeignKey(blank=True, help_text='If set, rule applies only to this station. Leave blank for all stations.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alert_rules', to='weather.weatherstation')),
            ],
            options={
                'verbose_name': 'Alert Rule',
                'verbose_name_plural': 'Alert Rules',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='AlertEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('triggered_at', models.DateTimeField(auto_now_add=True)),
                ('notify_status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('notify_sent_at', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True, default='')),
                ('observation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alert_events', to='weather.weatherobservation')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='alerts.alertrule')),
            ],
            options={
                'verbose_name': 'Alert Event',
                'verbose_name_plural': 'Alert Events',
                'ordering': ['-triggered_at'],
            },
        ),
    ]
