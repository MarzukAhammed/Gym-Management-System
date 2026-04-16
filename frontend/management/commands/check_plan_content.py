from django.core.management.base import BaseCommand
from frontend.models import Plan

class Command(BaseCommand):
    help = 'Check plan content in database'

    def handle(self, *args, **options):
        plans = Plan.objects.all()
        for plan in plans:
            self.stdout.write(f'ID: {plan.id} | Title: {plan.title}')
            self.stdout.write(f'Description preview: {plan.description[:50]}...')
            self.stdout.write('---')
