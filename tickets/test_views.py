import json

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Seminar, Cart, CartItem, Order, DiscountCode
from django.utils import timezone

class CartViewTests(TestCase):

    def setUp(self):
        self.client = Client()
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
        self.client.login(username='testuser', password='12345')

    def test_add_to_cart_reserves_seats(self):
        url = reverse('add_to_cart', kwargs={'seminar_id': self.seminar.id})
        response = self.client.post(url, {'quantity': 2})
        self.assertEqual(response.status_code, 200)
        self.seminar.refresh_from_db()
        self.assertEqual(self.seminar.reserved_seats, 2)
        self.assertEqual(self.seminar.remaining_seats, 8)

    def test_remove_from_cart_releases_seats(self):
        cart_item = CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=2)
        url_remove = reverse('remove_from_cart', kwargs={'item_id': cart_item.id})
        response = self.client.get(url_remove)
        self.assertEqual(response.status_code, 302)  # Expect a redirect
        self.seminar.refresh_from_db()
        self.assertEqual(self.seminar.reserved_seats, 0)
        self.assertEqual(self.seminar.remaining_seats, 10)

    def test_apply_discount(self):
        discount_code = DiscountCode.objects.create(
            code='TESTCODE',
            discount_percentage=10,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timezone.timedelta(days=1),
            usage_limit=5
        )
        cart_item = CartItem.objects.create(cart=self.cart, seminar=self.seminar, quantity=2)
        url = reverse('apply_discount')
        response = self.client.post(url, json.dumps({'discount_code': 'TESTCODE'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['new_total'], 'Rp 180.000')

class CheckoutViewTests(TestCase):

    def setUp(self):
        self.client = Client()
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
        self.client.login(username='testuser', password='12345')

    def test_checkout_view_get(self):
        url = reverse('checkout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Seminar')
        self.assertContains(response, '200.00')

    def test_checkout_view_post(self):
        url = reverse('checkout')
        response = self.client.post(url, {'final_total': '200.00'})
        self.assertRedirects(response, reverse('order_confirmed'))
        self.assertFalse(CartItem.objects.filter(cart=self.cart).exists())
        self.seminar.refresh_from_db()
        self.assertEqual(self.seminar.available_seats, 8)
        self.assertEqual(self.seminar.reserved_seats, 0)
