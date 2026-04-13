from django.shortcuts import redirect


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
