"""Management command to seed stations, sample incidents, and fetch real weather data."""
from django.core.management.base import BaseCommand

from apps.ingestion.services import ingest_all_active_stations, seed_default_stations, seed_sample_incidents


class Command(BaseCommand):
    help = "Seeds default stations, sample incidents, and ingests latest weather observations from Open-Meteo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-fetch",
            action="store_true",
            help="Seed stations and incidents only, without calling the external API.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding default weather stations..."))
        stations = seed_default_stations()
        self.stdout.write(self.style.SUCCESS(f"Registered {len(stations)} stations."))

        self.stdout.write(self.style.NOTICE("Seeding sample incident hazard polygons..."))
        seed_sample_incidents()
        self.stdout.write(self.style.SUCCESS("Sample incidents initialized."))

        if not options["no_fetch"]:
            self.stdout.write(self.style.NOTICE("Ingesting live & historical observations from Open-Meteo..."))
            result = ingest_all_active_stations()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Done! Processed {result.get('total_records_processed', 0)} records across {result.get('stations_polled', 0)} stations."
                )
            )
