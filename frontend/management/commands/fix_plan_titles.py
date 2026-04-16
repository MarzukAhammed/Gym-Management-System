from django.core.management.base import BaseCommand
from frontend.models import Plan

class Command(BaseCommand):
    help = 'Fix plan titles to be English-only'

    def handle(self, *args, **options):
        plans = Plan.objects.all()
        
        # Mapping of current mixed titles to clean English titles
        title_mapping = {
            'বেসিক মেম্বারশিপ (Basic Membership)': 'Basic Membership',
            'প্রিমিয়াম মেম্বারশিপ (Premium Membership)': 'Premium Membership', 
            'আল্টিমেট মেম্বারশিপ (Ultimate Membership)': 'Ultimate Membership'
        }
        
        updated_count = 0
        for plan in plans:
            if plan.title in title_mapping:
                new_title = title_mapping[plan.title]
                plan.title = new_title
                plan.duration = '1 Month'
                plan.save()
                updated_count += 1
                self.stdout.write(f'Updated plan: {new_title}')
        
        self.stdout.write(f'Successfully updated {updated_count} plans')
