import datetime
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
