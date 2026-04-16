from django.core.management.base import BaseCommand
from frontend.models import Plan

class Command(BaseCommand):
    help = 'Check current plan descriptions'

    def handle(self, *args, **options):
        plans = Plan.objects.all()
        for plan in plans:
            self.stdout.write(f'Plan: {plan.title}')
            self.stdout.write(f'Description: {plan.description}')
            self.stdout.write('---')
