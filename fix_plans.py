import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_project.settings')
django.setup()

from frontend.models import Plan

# Check existing plans
plans = Plan.objects.all()
print(f'Found {len(plans)} plans:')
for plan in plans:
    print(f'ID: {plan.id} - Title: {plan.title}')

# Update plan titles to clean English
plan_title_mapping = {
    'বেসিক মেম্বারশিপ (Basic Membership)': 'Basic Membership',
    'প্রিমিয়াম মেম্বারশিপ (Premium Membership)': 'Premium Membership',
    'আল্টিমেট মেম্বারশিপ (Ultimate Membership)': 'Ultimate Membership'
}

updated_count = 0
for plan in plans:
    if plan.title in plan_title_mapping:
        print(f'Updating: {plan.title} -> {plan_title_mapping[plan.title]}')
        plan.title = plan_title_mapping[plan.title]
        plan.duration = '1 Month'
        plan.save()
        updated_count += 1

print(f'Updated {updated_count} plans successfully!')
