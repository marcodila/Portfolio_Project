"""
Management command: python manage.py seed_initial_projects

Always loads the initial_projects fixture (upsert — updates existing records,
inserts new ones). This keeps Render's database in sync with the committed
fixture on every deploy.

Workflow: edit data locally → dumpdata → commit → push → Render stays current.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Load initial_projects fixture on every deploy (upsert, never deletes).'

    def handle(self, *args, **options):
        call_command('loaddata', 'initial_projects')
        self.stdout.write(self.style.SUCCESS('Fixture loaded successfully.'))
