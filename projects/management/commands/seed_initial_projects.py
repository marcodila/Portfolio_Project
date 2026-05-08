"""
Management command: python manage.py seed_initial_projects

Loads the initial_projects fixture ONLY if the projects table is empty.
This prevents overwriting projects added or edited via the admin panel
on subsequent deploys.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from projects.models import Project


class Command(BaseCommand):
    help = 'Seed initial projects fixture only on first deploy (skips if data exists).'

    def handle(self, *args, **options):
        if Project.objects.exists():
            self.stdout.write('Projects already exist — skipping seed.')
            return
        call_command('loaddata', 'initial_projects')
        self.stdout.write(self.style.SUCCESS(
            f'Seeded {Project.objects.count()} initial projects.'
        ))
