from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView

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
