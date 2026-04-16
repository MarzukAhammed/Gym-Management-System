# Generated migration for Bangladesh membership plans
from django.db import migrations

def create_bangladesh_plans(apps, schema_editor):
    Plan = apps.get_model('frontend', 'Plan')
    
    plans_data = [
        {
            'title': 'Basic Membership',
            'price': 999.00,
            'duration': '1 Month',
            'description': '''<p>🏋️‍♂️ Basic gym access</p>
<p>📱 Mobile app usage</p>
<p>📊 Basic progress tracking</p>
<p>⏰ Anytime gym access</p>
<p>🇧🇩 Affordable for Bangladesh</p>'''
        },
        {
            'title': 'Premium Membership',
            'price': 1999.00,
            'duration': '1 Month',
            'description': '''<p>🏋️‍♂️ Unlimited gym access</p>
<p>📱 Premium mobile app features</p>
<p>👨‍⚕️ Personal trainer support</p>
<p>📊 Detailed progress reports</p>
<p>🎯 Customized workout plans</p>
<p>🥗 Diet planning support</p>
<p>⏰ VIP timing slots</p>'''
        },
        {
            'title': 'Ultimate Membership',
            'price': 3499.00,
            'duration': '1 Month',
            'description': '''<p>🏋️‍♂️ Unlimited gym access</p>
<p>📱 Ultimate mobile app</p>
<p>👨‍⚕️ 1-on-1 personal training</p>
<p>📊 Advanced analytics</p>
<p>🎯 Custom meal plans</p>
<p>🥗 Supplement guidance</p>
<p>⏰ Priority access anytime</p>
<p>🏆 Monthly challenge access</p>
<p>🎁 Exclusive merchandise discounts</p>'''
        }
    ]
    
    # Clear existing plans and create new ones
    Plan.objects.all().delete()
    for plan_data in plans_data:
        Plan.objects.create(**plan_data)

def reverse_create_bangladesh_plans(apps, schema_editor):
    Plan = apps.get_model('frontend', 'Plan')
    Plan.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('frontend', '0029_exercise_calories_per_minute_and_more'),
    ]

    operations = [
        migrations.RunPython(create_bangladesh_plans, reverse_create_bangladesh_plans),
    ]
