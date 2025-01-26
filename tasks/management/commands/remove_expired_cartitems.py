from django.core.management.base import BaseCommand
from tickets.models import CartItem  # Ensure this is the correct model import
from datetime import timedelta
from django.utils.timezone import now


class Command(BaseCommand):
    help = "Remove expired cart items that have been in the cart for over 24 hours."

    def handle(self, *args, **kwargs):
        # Update the field name to 'added_at'
        expired_items = CartItem.objects.filter(added_at__lte=now() - timedelta(hours=24))
        count = expired_items.count()
        expired_items.delete()
        self.stdout.write(f"Successfully removed {count} expired cart items.")
