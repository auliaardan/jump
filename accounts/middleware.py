from django.shortcuts import redirect
from django.urls import reverse

class RequireProfileCompleteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            # Check if user’s required fields are missing:
            if not all([
                user.nama_lengkap,
                user.nik,
                user.institution,
                user.Nomor_telpon,
            ]):
                complete_profile_url = reverse("complete_profile")
                if request.path != complete_profile_url:
                    return redirect("complete_profile")

        return self.get_response(request)
