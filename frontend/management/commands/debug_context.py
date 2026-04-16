from django.core.management.base import BaseCommand
from django.utils import translation

class Command(BaseCommand):
    help = 'Debug context processor'

    def handle(self, *args, **options):
        current_language = translation.get_language()
        self.stdout.write(f'Current language: {current_language}')
        self.stdout.write(f'Available languages: {translation.get_languages()}')
