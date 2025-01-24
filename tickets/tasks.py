from celery import shared_task

@shared_task
def remove_expired_cartitems():
    from .models import CartItem
    from datetime import timedelta
    from django.utils.timezone import now

    expiration_time = now() - timedelta(hours=24)
    CartItem.objects.filter(created_at__lt=expiration_time).delete()