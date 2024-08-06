# tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from .models import Seminar, Cart, CartItem, Order

User = get_user_model()


class SeminarSeatManagementTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')  # Ensure user is logged in
        self.seminar = Seminar.objects.create(
            title='Test Seminar',
            description='Test Description',
            available_seats=5,
            price=10.00,
            date=timezone.now(),  # Add a valid date
            category=Seminar.SEMINAR
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_seminar_remaining_seats(self):
        self.assertEqual(self.seminar.remaining_seats, 5)

    def test_add_to_cart_reserves_seats(self):
        CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=2)
        self.seminar.refresh_from_db()
        self.assertEqual(self.seminar.remaining_seats, 3)

    def test_remove_from_cart_releases_seats(self):
        cart_item = CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=2)
        cart_item.delete()
        self.seminar.refresh_from_db()
        self.assertEqual(self.seminar.remaining_seats, 5)

    def test_confirm_order_reduces_available_seats(self):
        cart_item = CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=3)
        order = Order.objects.create(user=self.user)
        order.seminars.add(self.seminar)
        order.is_confirmed = True
        order.save()
        self.seminar.refresh_from_db()
        self.assertEqual(self.seminar.available_seats, 2)
        self.assertEqual(self.seminar.reserved_seats, 0)

    def test_add_to_cart_more_than_available(self):
        response = self.client.post(reverse('add_to_cart', args=[self.seminar.id]), {'quantity': 6})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Not enough remaining seats'})
        self.seminar.refresh_from_db()
        self.assertEqual(self.seminar.remaining_seats, 5)

    def test_checkout_deletes_cart_items(self):
        CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=2)
        response = self.client.post(reverse('checkout'), {'final_total': '20.00'})
        self.assertEqual(response.status_code, 302)  # Redirect to order_confirmed
        self.assertFalse(CartItem.objects.filter(cart=self.cart).exists())

    def test_seminar_reserved_seats_in_cart(self):
        CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=2)
        self.assertEqual(self.seminar.reserved_seats_in_cart, 2)

    def test_cart_item_signal_reserve_seats_on_save(self):
        cart_item = CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=3)
        self.seminar.refresh_from_db()
        self.assertEqual(self.seminar.reserved_seats, 3)

    def test_cart_item_signal_release_seats_on_delete(self):
        cart_item = CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=2)
        cart_item.delete()
        self.seminar.refresh_from_db()
        self.assertEqual(self.seminar.reserved_seats, 0)

    def test_cart_item_signal_update_quantity(self):
        cart_item = CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=1)
        cart_item.quantity = 3
        cart_item.save()
        self.seminar.refresh_from_db()
        self.assertEqual(self.seminar.reserved_seats, 3)


if __name__ == '__main__':
    unittest.main()
