import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import FileExtensionValidator
from django.utils import timezone

from .models import PaymentProof, AcceptedAbstractSubmission
from .models import SciComSubmission, TicketCategory

User = get_user_model()

SCICOM_MEDIA_SUBMISSION_DEADLINE = datetime.datetime(2026, 6, 6, 0, 0)
SCICOM_MEDIA_DEADLINE_LABEL = "5 June 2026"
SCICOM_ABSTRACT_CLOSED_MESSAGE = "Abstract submissions via the website are now closed."


def get_scicom_media_submission_deadline():
    return timezone.make_aware(
        SCICOM_MEDIA_SUBMISSION_DEADLINE,
        timezone.get_current_timezone(),
    )


def is_scicom_media_submission_open():
    return timezone.now() < get_scicom_media_submission_deadline()


class SciComSubmissionForm(forms.ModelForm):
    class Meta:
        model = SciComSubmission
        fields = [
            'submission_type',
            'address',
            'occupation',
            'abstract_title',
            'paper_type',
            'abstract_authors',
            'abstract_text',
            'link_abstract',
            'video_title',
            'video_authors',
            'link_video',
            'flyer_title',
            'flyer_authors',
            'link_flyer',
        ]

        widgets = {
            'abstract_authors': forms.Textarea(attrs={'rows': 2}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'abstract_authors': forms.Textarea(attrs={'rows': 2}),
            'video_authors': forms.Textarea(attrs={'rows': 2}),
            'flyer_authors': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['submission_type'].choices = [
            choice for choice in SciComSubmission.SUBMISSION_TYPE_CHOICES
            if choice[0] in (SciComSubmission.VIDEO, SciComSubmission.FLYER)
        ]
        self.fields['submission_type'].help_text = (
            f"Abstract submissions via the website are closed. "
            f"Educative Video and Educative Flyer submissions are accepted until "
            f"{SCICOM_MEDIA_DEADLINE_LABEL}."
        )

        # Figure out the submission_type
        if 'submission_type' in self.data:
            submission_type = self.data.get('submission_type')
        else:
            submission_type = self.initial.get('submission_type') or getattr(self.instance, 'submission_type', None)

        if not submission_type or (not self.data and submission_type == SciComSubmission.ABSTRACT):
            submission_type = SciComSubmission.VIDEO
            self.initial['submission_type'] = submission_type

        if submission_type == SciComSubmission.ABSTRACT:
            # Remove video fields
            for fieldname in ["video_title", "video_authors", "link_video"]:
                if fieldname in self.fields:
                    del self.fields[fieldname]
            # Remove flyer fields
            for fieldname in ["flyer_title", "flyer_authors", "link_flyer"]:
                if fieldname in self.fields:
                    del self.fields[fieldname]

        elif submission_type == SciComSubmission.VIDEO:
            # Remove abstract
            for fieldname in ["abstract_title", "paper_type", "abstract_authors", "abstract_text", "link_abstract"]:
                if fieldname in self.fields:
                    del self.fields[fieldname]
            # Remove flyer
            for fieldname in ["flyer_title", "flyer_authors", "link_flyer"]:
                if fieldname in self.fields:
                    del self.fields[fieldname]

        elif submission_type == SciComSubmission.FLYER:
            # Remove abstract
            for fieldname in ["abstract_title", "paper_type", "abstract_authors", "abstract_text", "link_abstract"]:
                if fieldname in self.fields:
                    del self.fields[fieldname]
            # Remove video
            for fieldname in ["video_title", "video_authors", "link_video"]:
                if fieldname in self.fields:
                    del self.fields[fieldname]

    def clean_submission_type(self):
        submission_type = self.cleaned_data.get('submission_type')
        if submission_type == SciComSubmission.ABSTRACT:
            raise forms.ValidationError(SCICOM_ABSTRACT_CLOSED_MESSAGE)
        if (
            submission_type in (SciComSubmission.VIDEO, SciComSubmission.FLYER)
            and not is_scicom_media_submission_open()
        ):
            raise forms.ValidationError(
                f"Video and flyer submissions closed after {SCICOM_MEDIA_DEADLINE_LABEL}."
            )
        return submission_type


class AcceptedAbstractForm(forms.ModelForm):
    class Meta:
        model = AcceptedAbstractSubmission
        fields = ['abstract', 'ppt_link', 'poster_link']
        widgets = {
            'abstract': forms.Select(attrs={'class': 'form-control'}),
            'ppt_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://…'}),
            'poster_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only the abstract_title instead of the default __str__()
        self.fields['abstract'].label_from_instance = lambda obj: obj.abstract_title

    def clean(self):
        cleaned_data = super().clean()
        ppt_link = cleaned_data.get('ppt_link')
        poster_link = cleaned_data.get('poster_link')
        if not ppt_link and not poster_link:
            raise forms.ValidationError(
                "Please provide at least one link (PPT or poster)."
            )
        return cleaned_data


class ManualTicketUploadForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="User",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the user who should receive the confirmed ticket email.",
    )
    ticket_category = forms.ModelChoiceField(
        queryset=TicketCategory.objects.none(),
        label="Seminar / Workshop ticket",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
    )
    payment_proof = forms.FileField(
        label="Payment proof",
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf'])
        ],
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,application/pdf,.pdf',
        }),
        help_text="Upload the buyer's payment proof before creating confirmed tickets.",
    )
    price_paid = forms.DecimalField(
        label="Amount paid",
        max_digits=12,
        decimal_places=0,
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        help_text="Leave blank to use the ticket total.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.order_by('nama_lengkap', 'username')
        self.fields['ticket_category'].queryset = (
            TicketCategory.objects.select_related('seminar')
            .order_by('seminar__date', 'seminar__title', 'name')
        )

    def clean(self):
        cleaned_data = super().clean()
        ticket_category = cleaned_data.get('ticket_category')
        quantity = cleaned_data.get('quantity')

        if ticket_category and quantity and ticket_category.remaining_seats < quantity:
            raise forms.ValidationError(
                f"Only {ticket_category.remaining_seats} seat(s) remain for {ticket_category}."
            )

        return cleaned_data


class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = PaymentProof
        fields = ['proof']
        widgets = {
            'proof': forms.ClearableFileInput(attrs={'accept': 'image/*,application/pdf,.pdf'}),
        }
        labels = {
            'proof': 'Payment proof (image or PDF)',
        }


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']
