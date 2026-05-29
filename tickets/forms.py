import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import PaymentProof, AcceptedAbstractSubmission
from .models import SciComSubmission

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
