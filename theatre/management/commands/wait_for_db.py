import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until a database is available."""

    def handle(self, *args, **options):
        """Handle the command by checking database connection."""
        self.stdout.write("Waiting for database...")
        db_conn = False
        attempts = 0
        while not db_conn:
            try:
                connections["default"].cursor()
                db_conn = True
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                attempts += 1
                time.sleep(1)
                if attempts > 45:
                    self.stdout.write(
                        self.style.ERROR("Database unavailable.")
                    )
                    break
        self.stdout.write(self.style.SUCCESS("Database available!"))
