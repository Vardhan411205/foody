from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix migration history issues'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Delete problematic migration records
            cursor.execute("DELETE FROM django_migrations WHERE app = 'joo' OR app = 'auth';")
            self.stdout.write(self.style.SUCCESS('Successfully removed migration records')) 