from celery import shared_task
from .models import CartItem
from datetime import timedelta
from django.utils.timezone import now

@shared_task
def remove_expired_cartitems():
    threshold = now() - timedelta(hours=24)
    CartItem.objects.filter(created_at__lt=threshold).delete()
