from .models import Payment


def navbar_notifications(request):
    if not request.user.is_authenticated:
        return {"navbar_notifications": [], "unread_notification_count": 0}

    notifications = []
    username = request.user.username

    latest_verified = Payment.objects.filter(
        full_name__iexact=username,
        verified=True
    ).order_by("-created_at").first()

    latest_pending = Payment.objects.filter(
        full_name__iexact=username,
        verified=False
    ).order_by("-created_at").first()

    if latest_verified:
        notifications.append({
            "type": "success",
            "text": f"Your payment of {latest_verified.amount} BDT is verified.",
        })
    elif latest_pending:
        notifications.append({
            "type": "warning",
            "text": "Your payment is under admin review.",
        })

    notifications.append({
        "type": "info",
        "text": "Check your profile for latest membership updates.",
    })

    unread = sum(1 for n in notifications if n["type"] != "info")
    return {
        "navbar_notifications": notifications[:5],
        "unread_notification_count": unread,
    }
