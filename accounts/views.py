from django.conf import settings
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.views.generic.edit import FormView

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = "registration/signup.html"

class CompleteProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "registration/complete_profile.html"
    success_url = reverse_lazy("seminar_list")  # or wherever you want

    def get_object(self, queryset=None):
        # Ensure that the form edits the currently logged-in user
        return self.request.user


class SitePasswordResetView(PasswordResetView):
    extra_email_context = {"site_name": settings.SITE_NAME}

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
            "domain_override": settings.SITE_DOMAIN,
        }
        form.save(**opts)
        return FormView.form_valid(self, form)
