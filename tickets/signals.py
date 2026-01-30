import os

from django.core.mail import EmailMessage
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import seminars_page, about_us, workshops_page, PaymentProof, Seminar, SciComSubmission


@receiver(post_delete, sender=seminars_page)
def delete_media_files_seminars(sender, instance, **kwargs):
    image_fields = [
        instance.image_section_two_top_left,
        instance.image_section_two_top_right,
        instance.image_section_two_bot_left,
        instance.image_section_two_bot_right,
    ]

    for image_field in image_fields:
        if image_field:
            image_path = image_field.path
            if os.path.isfile(image_path):
                os.remove(image_path)


@receiver(post_delete, sender=about_us)
def delete_media_files_about_us(sender, instance, **kwargs):
    image_fields = [
        instance.image_section_two,

    ]

    for image_field in image_fields:
        if image_field:
            image_path = image_field.path
            if os.path.isfile(image_path):
                os.remove(image_path)


@receiver(post_delete, sender=workshops_page)
def delete_media_files_workshop_page(sender, instance, **kwargs):
    image_fields = [
        instance.image_section_two_top_left,
        instance.image_section_two_top_right,
        instance.image_section_two_bot_left,
        instance.image_section_two_bot_right,
    ]

    for image_field in image_fields:
        if image_field:
            image_path = image_field.path
            if os.path.isfile(image_path):
                os.remove(image_path)


@receiver(post_delete, sender=PaymentProof)
def delete_media_files_paymentProof(sender, instance, **kwargs):
    image_fields = [
        instance.proof
    ]

    for image_field in image_fields:
        if image_field:
            image_path = image_field.path
            if os.path.isfile(image_path):
                os.remove(image_path)


@receiver(post_delete, sender=Seminar)
def delete_media_files_sem(sender, instance, **kwargs):
    image_fields = [
        instance.image
    ]

    for image_field in image_fields:
        if image_field:
            image_path = image_field.path
            if os.path.isfile(image_path):
                os.remove(image_path)


@receiver(pre_save, sender=SciComSubmission)
def cache_old_acceptance_state(sender, instance, **kwargs):
    """
    Attach the old is_accepted state to the instance, so we can compare in post_save.
    """
    if instance.pk:
        try:
            old = SciComSubmission.objects.get(pk=instance.pk)
            instance._old_is_accepted = old.is_accepted
        except SciComSubmission.DoesNotExist:
            instance._old_is_accepted = False
    else:
        instance._old_is_accepted = False


@receiver(post_save, sender=SciComSubmission)
def send_acceptance_email(sender, instance, created, **kwargs):
    """
    After saving, if an existing submission just flipped to is_accepted=True,
    render the HTML template (which already has a header image) and send it.
    """
    # Only proceed when this was an update to an existing record
    if created:
        return

    old_state = getattr(instance, '_old_is_accepted', False)
    new_state = instance.is_accepted

    # If it changed from False → True, send the “accepted” email
    if not old_state and new_state:
        # Prepare context for the email template
        context = {
            'name': instance.user.nama_lengkap,
            'abstract_title': instance.abstract_title,
            'type': instance.get_submission_type_display(),
            'submission_link': "https://jakartaurologymedicalupdate.com/submission/accepted/",
        }

        # Render the HTML body (the template already includes the header image)
        email_body = render_to_string('tickets/emails/accepted_notification.html',
                                      context)  # :contentReference[oaicite:0]{index=0}

        # Compose and send the EmailMessage
        email_subject = "Announcement of Abstract Selection – JUMP 2026 Scientific Competition"
        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email='admin@jakartaurologymedicalupdate.com',  # adjust as needed
            to=[instance.user.email],
        )
        email.content_subtype = 'html'  # ensures the HTML template is rendered
        email.send(fail_silently=False)
