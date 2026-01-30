from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import PaymentProof, AcceptedAbstractSubmission
from .models import SciComSubmission


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

        # Figure out the submission_type
        if 'submission_type' in self.data:
            submission_type = self.data.get('submission_type')
        else:
            submission_type = self.initial.get('submission_type') or getattr(self.instance, 'submission_type', None)

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
