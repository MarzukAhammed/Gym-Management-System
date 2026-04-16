import datetime
from django.utils import translation
from django.utils.safestring import mark_safe
from .models import Payment, UserProgress, Notification


def _calculate_workout_streak(user):
    logs = UserProgress.objects.filter(user=user).order_by("-date")
    if not logs.exists():
        return 0

    workout_dates = []
    seen = set()
    for log in logs:
        if log.date not in seen:
            seen.add(log.date)
            workout_dates.append(log.date)

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    latest = workout_dates[0]

    # Streak is active only if latest workout is today or yesterday.
    if latest not in {today, yesterday}:
        return 0

    streak = 1
    prev_day = latest
    for d in workout_dates[1:]:
        if d == (prev_day - datetime.timedelta(days=1)):
            streak += 1
            prev_day = d
        else:
            break
    return streak


def navbar_notifications(request):
    if not request.user.is_authenticated:
        return {"navbar_notifications": [], "unread_notification_count": 0}

    qs = Notification.objects.filter(user=request.user)
    unread = qs.filter(is_read=False).count()
    visible = list(qs.all()[:8])
    return {
        "navbar_notifications": visible,
        "unread_notification_count": unread,
    }


def plan_translations(request):
    """
    Provide Bengali translations for membership plans when language is Bengali
    """
    current_language = translation.get_language()
    # Check if language starts with 'bn' (handles 'bn', 'bn-bd', etc.)
    is_bengali = current_language.startswith('bn')
    
    # Bengali translations for plan titles and descriptions
    bengali_translations = {
        'Basic Membership': {
            'title': 'বেসিক মেম্বারশিপ (Basic Membership)',
            'description': '''🏋️‍♂️ বেসিক জিম অ্যাক্সেস
📱 মোবাইল অ্যাপ ব্যবহারের সুবিধা
📊 বেসিক প্রোগ্রেস ট্র্যাকিং
⏰ যেকোনো সময় জিমে প্রবেশের সুবিধা
🇧🇩 বাংলাদেশের জন্য সাশ্রয়ী মূল্য'''
        },
        'Premium Membership': {
            'title': 'প্রিমিয়াম মেম্বারশিপ (Premium Membership)',
            'description': '''🏋️‍♂️ আনলিমিটেড জিম অ্যাক্সেস
📱 প্রিমিয়াম মোবাইল অ্যাপ ফিচার
👨‍⚕️ পার্সোনাল ট্রেইনার সাপোর্ট
📊 ডিটেইলড প্রোগ্রেস রিপোর্ট
🎯 কাস্টমাইজড ওয়ার্কআউট প্ল্যান
🥗 ডায়েট প্ল্যানিং সাপোর্ট
⏰ VIP টাইমিং স্লট'''
        },
        'Ultimate Membership': {
            'title': 'আল্টিমেট মেম্বারশিপ (Ultimate Membership)',
            'description': '''🏋️‍♂️ আনলিমিটেড জিম অ্যাক্সেস
📱 আল্টিমেট মোবাইল অ্যাপ
👨‍⚕️ ১-অন-১ পার্সোনাল ট্রেইনিং
📊 অ্যাডভান্সড অ্যানালিটিক্স
🎯 কাস্টম মিল ডায়েট প্ল্যান
🥗 সাপ্লিমেন্ট গাইডেন্স
⏰ যেকোনো সময় প্রায়োরিটি অ্যাক্সেস
🏆 মাসিক চ্যালেঞ্জ অ্যাক্সেস
🎁 এক্সক্লুসিভ মার্চেন্ডাইজ ডিসকাউন্ট'''
        }
    }
    
    return {
        'PLAN_TRANSLATIONS': bengali_translations if is_bengali else {},
        'CURRENT_LANG': current_language
    }
