from django.core.management.base import BaseCommand
from frontend.models import Plan

class Command(BaseCommand):
    help = 'Fix plan descriptions to be English-only HTML'

    def handle(self, *args, **options):
        plans = Plan.objects.all()
        
        # Clean English descriptions with proper HTML
        english_descriptions = {
            'Basic Membership': '''<p>🏋️‍♂️ Basic gym access</p>
<p>📱 Mobile app usage</p>
<p>📊 Basic progress tracking</p>
<p>⏰ Anytime gym access</p>
<p>🇧🇩 Affordable for Bangladesh</p>''',
            'Premium Membership': '''<p>🏋️‍♂️ Unlimited gym access</p>
<p>📱 Premium mobile app features</p>
<p>👨‍⚕️ Personal trainer support</p>
<p>📊 Detailed progress reports</p>
<p>🎯 Customized workout plans</p>
<p>🥗 Diet planning support</p>
<p>⏰ VIP timing slots</p>''',
            'Ultimate Membership': '''<p>🏋️‍♂️ Unlimited gym access</p>
<p>📱 Ultimate mobile app</p>
<p>👨‍⚕️ 1-on-1 personal training</p>
<p>📊 Advanced analytics</p>
<p>🎯 Custom meal plans</p>
<p>🥗 Supplement guidance</p>
<p>⏰ Priority access anytime</p>
<p>🏆 Monthly challenge access</p>
<p>🎁 Exclusive merchandise discounts</p>'''
        }
        
        updated_count = 0
        for plan in plans:
            if plan.title in english_descriptions:
                plan.description = english_descriptions[plan.title]
                plan.save()
                updated_count += 1
                self.stdout.write(f'Updated description for: {plan.title}')
        
        self.stdout.write(f'Successfully updated {updated_count} plan descriptions')
