from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import os

class Command(BaseCommand):
    help = 'Setup database tables and initial data'

    def handle(self, *args, **kwargs):
        try:
            # Remove old migrations
            migrations_dir = 'joo/migrations'
            for file in os.listdir(migrations_dir):
                if file.startswith('0') and file.endswith('.py'):
                    os.remove(os.path.join(migrations_dir, file))
            self.stdout.write('Removed old migrations')

            # Drop existing tables if they exist
            with connection.cursor() as cursor:
                cursor.execute("""
                    DROP TABLE IF EXISTS joo_fooditem CASCADE;
                    DROP TABLE IF EXISTS django_migrations CASCADE;
                """)
            self.stdout.write('Dropped existing tables')

            # Make new migrations
            call_command('makemigrations', 'joo')
            self.stdout.write('Created new migrations')

            # Apply migrations with sync
            call_command('migrate', '--run-syncdb')
            self.stdout.write('Applied migrations')

            self.stdout.write(self.style.SUCCESS('Successfully setup database'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 