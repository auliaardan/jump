import os

from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Profile, landing_page, seminars_page, about_us


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_delete, sender=landing_page)
def delete_media_files(sender, instance, **kwargs):
    image_fields = [
        instance.image_section_one,
        instance.image_section_two_left,
        instance.image_section_two_right,
        instance.image_section_three_left,
        instance.image_section_three_right
    ]

    for image_field in image_fields:
        if image_field:
            image_path = image_field.path
            if os.path.isfile(image_path):
                os.remove(image_path)


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
