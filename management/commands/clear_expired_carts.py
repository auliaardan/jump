# Create a file management/commands/clear_expired_carts.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from tickets.models import CartItem

class Command(BaseCommand):
    help = 'Clear expired carts and restore reserved seats'

    def handle(self, *args, **kwargs):
        expiry_time = timezone.now() - timezone.timedelta(days=1)
        expired_items = CartItem.objects.filter(added_at__lt=expiry_time)

        for item in expired_items:
            item.seminar.release_seats(item.quantity)
            item.delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleared expired carts and restored seats'))
