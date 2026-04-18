from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta


class AdminOnlySessionMiddleware:
    """
    Keep staff/admin users inside /admin area.
    If admin opens normal website pages, redirect to admin dashboard.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path or ""
        if (
            request.user.is_authenticated
            and request.user.is_staff
            and not path.startswith("/admin")
            and not path.startswith("/static/")
            and not path.startswith("/media/")
        ):
            return redirect("/admin/")
        return self.get_response(request)


class NotificationsFromMessagesMiddleware:
    """
    Convert Django messages (success/info/warning/error) into persistent Notification rows.
    This makes "top alerts" appear in the bell dropdown + history page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return response

        try:
            from .models import Notification
        except Exception:
            return response

        # Consume queued messages intentionally (we want them in the bell, not as page alerts).
        storage = messages.get_messages(request)
        for m in storage:
            level = getattr(m, "tags", "") or "info"
            level = (level.split() or ["info"])[0].strip().lower()
            if level not in {"success", "info", "warning", "error"}:
                level = "info"
            text = str(m.message or "").strip()
            if not text:
                continue
            # Prevent duplicate notifications: check if same user has same text within last 5 minutes
            five_minutes_ago = timezone.now() - timedelta(minutes=5)
            existing = Notification.objects.filter(
                user=request.user,
                text=text,
                created_at__gte=five_minutes_ago
            ).exists()
            if not existing:
                Notification.objects.create(user=request.user, level=level, text=text)

        return response
