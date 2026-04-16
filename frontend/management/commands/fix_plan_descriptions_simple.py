from django.core.management.base import BaseCommand
from frontend.models import Plan

class Command(BaseCommand):
    help = 'Fix plan descriptions to simple text without HTML'

    def handle(self, *args, **options):
        plans = Plan.objects.all()
        
        # Simple text descriptions without HTML
        simple_descriptions = {
            'Basic Membership': '''🏋️‍♂️ Basic gym access
📱 Mobile app usage
📊 Basic progress tracking
⏰ Anytime gym access
🇧🇩 Affordable for Bangladesh''',
            'Premium Membership': '''🏋️‍♂️ Unlimited gym access
📱 Premium mobile app features
👨‍⚕️ Personal trainer support
📊 Detailed progress reports
🎯 Customized workout plans
🥗 Diet planning support
⏰ VIP timing slots''',
            'Ultimate Membership': '''🏋️‍♂️ Unlimited gym access
📱 Ultimate mobile app
👨‍⚕️ 1-on-1 personal training
📊 Advanced analytics
🎯 Custom meal plans
🥗 Supplement guidance
⏰ Priority access anytime
🏆 Monthly challenge access
🎁 Exclusive merchandise discounts'''
        }
        
        updated_count = 0
        for plan in plans:
            if plan.title in simple_descriptions:
                plan.description = simple_descriptions[plan.title]
                plan.save()
                updated_count += 1
                self.stdout.write(f'Updated description for: {plan.title}')
        
        self.stdout.write(f'Successfully updated {updated_count} plan descriptions to simple text')
