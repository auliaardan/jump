from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Sesuai yang digunakan untuk plataran sehat',
        widget=forms.EmailInput(attrs={'placeholder': 'Sesuai yang digunakan untuk plataran sehat'}),
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "email",
            "nama_lengkap",
            "nik",
            "institution",
            "Nomor_telpon",
        )
        labels = {
            'nik': 'NIK',
            'institution': 'Institusi',
            'Nomor_telpon' : 'No. Telpon'
        }
        help_texts = {
            'nama_lengkap': 'Sesuai KTP beserta gelar lengkap',
        }
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={'placeholder': 'Nama lengkap sesuai KTP beserta gelar'}),
        }


class CustomUserChangeForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        help_text='Sesuai yang digunakan untuk plataran sehat',
        widget=forms.EmailInput(attrs={'placeholder': 'Sesuai yang digunakan untuk plataran sehat'}),
    )

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
        labels = {
            'nik': 'NIK',
            'institution': 'Institusi',
            'Nomor_telpon': 'No. Telpon'
        }
        help_texts = {
            'nama_lengkap': 'Sesuai KTP beserta gelar lengkap',
        }
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={'placeholder': 'Nama lengkap sesuai KTP beserta gelar'}),
        }