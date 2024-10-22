from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "nama_lengkap",
            "nik",
            "institution",
            "email",
            "Nomor_telpon",
        )
        help_texts = {
            'nama_lengkap': 'Sesuai KTP beserta gelar lengkap',
            'email': 'Sesuai yang digunakan untuk plataran sehat',
        }
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={'placeholder': 'Nama lengkap sesuai KTP beserta gelar'}),
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "nama_lengkap",
            "nik",
            "institution",
            "email",
            "Nomor_telpon",
        )
        help_texts = {
            'nama_lengkap': 'Sesuai KTP beserta gelar lengkap',
            'email': 'Sesuai yang digunakan untuk plataran sehat'
        }
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={'placeholder': 'Nama lengkap sesuai KTP beserta gelar'}),
        }