from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


# Register your models here.

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "username",
        "nama_lengkap",
        "nik",
        "Nomor_telpon",
        "institution",
        "is_staff",
    ]
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("institution", "Nomor_telpon", "nama_lengkap", "nik",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("institution", "Nomor_telpon", "nama_lengkap", "nik",)}),)

admin.site.register(CustomUser, CustomUserAdmin)
