from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Test database connection'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            self.stdout.write(
                self.style.SUCCESS('✅ Database connection successful!')
            )
            self.stdout.write(f'Database: {settings.DATABASES["default"]["NAME"]}')
            self.stdout.write(f'Host: {settings.DATABASES["default"]["HOST"]}')
            self.stdout.write(f'Port: {settings.DATABASES["default"]["PORT"]}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Database connection failed: {e}')
            )
