from django.test import TestCase
from django.contrib.auth.models import User
from .models import Seminar, Cart, CartItem, Order, DiscountCode
from django.utils import timezone

class SeminarModelTests(TestCase):

    def setUp(self):
        self.seminar = Seminar.objects.create(
            title='Test Seminar',
            description='This is a test seminar.',
            date='2023-01-01 10:00:00',
            category='Seminar',
            price=100.00,
            available_seats=10
        )

    def test_seminar_reserve_seats(self):
        self.assertTrue(self.seminar.reserve_seats(5))
        self.assertEqual(self.seminar.reserved_seats, 5)
        self.assertEqual(self.seminar.remaining_seats, 5)

    def test_seminar_release_seats(self):
        self.seminar.reserve_seats(5)
        self.assertTrue(self.seminar.release_seats(3))
        self.assertEqual(self.seminar.reserved_seats, 2)
        self.assertEqual(self.seminar.remaining_seats, 8)

    def test_seminar_confirm_seats(self):
        self.seminar.reserve_seats(5)
        self.assertTrue(self.seminar.confirm_seats(3))
        self.assertEqual(self.seminar.available_seats, 7)
        self.assertEqual(self.seminar.reserved_seats, 2)
        self.assertEqual(self.seminar.remaining_seats, 5)

class CartModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.seminar = Seminar.objects.create(
            title='Test Seminar',
            description='This is a test seminar.',
            date='2023-01-01 10:00:00',
            category='Seminar',
            price=100.00,
            available_seats=10
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_add_to_cart(self):
        cart_item = CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=2)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.total_price(), 200.00)
        self.assertEqual(self.seminar.reserved_seats, 2)

    def test_remove_from_cart(self):
        cart_item = CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=2)
        cart_item.delete()
        self.assertEqual(self.seminar.reserved_seats, 0)

class OrderModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.seminar = Seminar.objects.create(
            title='Test Seminar',
            description='This is a test seminar.',
            date='2023-01-01 10:00:00',
            category='Seminar',
            price=100.00,
            available_seats=10
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=2)
        self.order = Order.objects.create(user=self.user)
        self.order.seminars.add(self.seminar)

    def test_confirm_order(self):
        self.order.is_confirmed = True
        self.order.save()
        self.order.refresh_from_db()
        self.assertEqual(self.seminar.available_seats, 8)
        self.assertEqual(self.seminar.reserved_seats, 0)

class DiscountCodeModelTests(TestCase):

    def setUp(self):
        self.discount_code = DiscountCode.objects.create(
            code='TESTCODE',
            discount_percentage=10,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timezone.timedelta(days=1),
            usage_limit=5
        )

    def test_is_valid(self):
        self.assertTrue(self.discount_code.is_valid())

    def test_apply_discount(self):
        total = 100.00
        discounted_total = self.discount_code.apply_discount(total)
        self.assertEqual(discounted_total, 90.00)
