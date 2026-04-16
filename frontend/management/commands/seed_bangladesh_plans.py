from django.core.management.base import BaseCommand
from frontend.models import Plan
import os

class Command(BaseCommand):
    help = 'Seed Bangladesh-specific gym membership plans'

    def handle(self, *args, **options):
        # Clear existing plans to avoid duplicates
        Plan.objects.all().delete()
        
        # Bangladesh-specific membership plans
        plans_data = [
            {
                'title': 'বেসিক মেম্বারশিপ (Basic Membership)',
                'price': 999.00,
                'duration': '1 মাস (1 Month)',
                'description': '''<p>🏋️‍♂️ বেসিক জিম অ্যাক্সেস</p>
<p>📱 মোবাইল অ্যাপ ব্যবহারের সুবিধা</p>
<p>📊 বেসিক প্রোগ্রেস ট্র্যাকিং</p>
<p>⏰ যেকোনো সময় জিমে প্রবেশের সুবিধা</p>
<p>🇧🇩 বাংলাদেশের জন্য সাশ্রয়ী মূল্য</p>'''
            },
            {
                'title': 'প্রিমিয়াম মেম্বারশিপ (Premium Membership)',
                'price': 1999.00,
                'duration': '1 মাস (1 Month)',
                'description': '''<p>🏋️‍♂️ আনলিমিটেড জিম অ্যাক্সেস</p>
<p>📱 প্রিমিয়াম মোবাইল অ্যাপ ফিচার</p>
<p>👨‍⚕️ পার্সোনাল ট্রেইনার সাপোর্ট</p>
<p>📊 ডিটেইলড প্রোগ্রেস রিপোর্ট</p>
<p>🎯 কাস্টমাইজড ওয়ার্কআউট প্ল্যান</p>
<p>🥗 ডায়েট প্ল্যানিং সাপোর্ট</p>
<p>⏰ VIP টাইমিং স্লট</p>'''
            },
            {
                'title': 'আল্টিমেট মেম্বারশিপ (Ultimate Membership)',
                'price': 3499.00,
                'duration': '1 মাস (1 Month)',
                'description': '''<p>🏋️‍♂️ আনলিমিটেড জিম অ্যাক্সেস</p>
<p>📱 আল্টিমেট মোবাইল অ্যাপ</p>
<p>👨‍⚕️ ১-অন-১ পার্সোনাল ট্রেইনিং</p>
<p>📊 অ্যাডভান্সড অ্যানালিটিক্স</p>
<p>🎯 কাস্টম মিল ডায়েট প্ল্যান</p>
<p>🥗 সাপ্লিমেন্ট গাইডেন্স</p>
<p>⏰ যেকোনো সময় প্রায়োরিটি অ্যাক্সেস</p>
<p>🏆 মাসিক চ্যালেঞ্জ অ্যাক্সেস</p>
<p>🎁 এক্সক্লুসিভ মার্চেন্ডাইজ ডিসকাউন্ট</p>'''
            }
        ]
        
        created_plans = []
        for plan_data in plans_data:
            plan = Plan.objects.create(**plan_data)
            created_plans.append(plan)
            # Minimal output to avoid Unicode issues
            self.stdout.write(f'Plan {len(created_plans)} created')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_plans)} Bangladesh membership plans')
        )
