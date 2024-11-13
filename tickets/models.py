from PIL import Image
from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import URLValidator
import os

from jump_project.settings import AUTH_USER_MODEL as User


class scicom_rules(models.Model):
    rule_name = models.TextField(blank=False, default="Sample Description")
    rule_description = models.TextField(blank=False, default="Sample Description")

    def get_description_lines(self):
        if self.rule_description:
            return self.rule_description.splitlines()
        else:
            return []


class qrcode(models.Model):
    link = models.URLField(blank=False,
                           default="https://www.example.com",
                           help_text="Enter a valid URL starting with http:// or https://")
    image = models.ImageField(upload_to="qrcode/", blank=False, null=False)

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


class PaymentMethod(models.Model):
    pay_method = models.TextField(blank=False, default="Sample Description")

    def __str__(self):
        return f"{self.pay_method}"


class workshops_page(models.Model):
    text_section_one = models.TextField(blank=False, default="Sample Description")
    text_section_two = models.TextField(blank=False, default="Sample Description")
    image_section_two_top_left = models.ImageField(upload_to='seminars_page_images/', )
    image_section_two_top_right = models.ImageField(upload_to='seminars_page_images/', )
    image_section_two_bot_left = models.ImageField(upload_to='seminars_page_images/', )
    image_section_two_bot_right = models.ImageField(upload_to='seminars_page_images/', )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        image_fields = [
            self.image_section_two_top_left,
            self.image_section_two_top_right,
            self.image_section_two_bot_left,
            self.image_section_two_bot_right,
        ]

        for image_field in image_fields:
            if image_field:
                self.compress_image(image_field)

    def compress_image(self, image_field):
        img = Image.open(image_field.path)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        img.save(image_field.path, 'JPEG', quality=85, optimize=True)


class seminars_page(models.Model):
    text_section_one = models.TextField(blank=False, default="Sample Description")
    text_section_two = models.TextField(blank=False, default="Sample Description")
    image_section_two_top_left = models.ImageField(upload_to='seminars_page_images/', )
    image_section_two_top_right = models.ImageField(upload_to='seminars_page_images/', )
    image_section_two_bot_left = models.ImageField(upload_to='seminars_page_images/', )
    image_section_two_bot_right = models.ImageField(upload_to='seminars_page_images/', )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        image_fields = [
            self.image_section_two_top_left,
            self.image_section_two_top_right,
            self.image_section_two_bot_left,
            self.image_section_two_bot_right,
        ]

        for image_field in image_fields:
            if image_field:
                self.compress_image(image_field)

    def compress_image(self, image_field):
        img = Image.open(image_field.path)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        img.save(image_field.path, 'JPEG', quality=85, optimize=True)


class WelcomingSpeech(models.Model):
    title = models.TextField(blank=False, default="Sample Description")
    image = models.ImageField(upload_to='about_us/', )
    name = models.TextField(blank=False, default="Sample Description")
    speech = models.TextField(blank=False, default="Sample Description")

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            self.compress_image(self.image)

    def compress_image(self, image_field):
        img = Image.open(image_field.path)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        img.save(image_field.path, 'JPEG', quality=85, optimize=True)

    def delete(self, *args, **kwargs):
        # Delete the image file when the instance is deleted
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


class sponsors(models.Model):
    SILVER = 'Silver'
    PLATINUM = 'Platinum'
    CATEGORY_CHOICES = [
        (SILVER, 'Silver'),
        (PLATINUM, 'Platinum'),
    ]

    sponsor_name = models.TextField(blank=False, default="Sample Description")
    sponsor_image = models.ImageField(upload_to='sponsor_images/', )
    sponsor_category = models.CharField(max_length=8, choices=CATEGORY_CHOICES, default=SILVER)


class landing_page(models.Model):
    header_section_one = models.TextField(blank=False, default="Sample Description")
    text_section_one = models.TextField(blank=False, default="Sample Description")
    image_section_one = models.ImageField(upload_to='landingpage_images/', )
    # Welcoming Message
    welcoming = models.ManyToManyField(WelcomingSpeech, blank=True)
    # Section 2
    header_section_two = models.CharField(max_length=100, blank=False, default="Sample Description")
    text_section_two = models.TextField(blank=False, default="Sample Description")
    image_section_two_left = models.ImageField(upload_to='landingpage_images/', )
    image_section_two_header_left = models.CharField(max_length=100, blank=False, default="Sample Description")
    image_section_two_text_left = models.CharField(max_length=100, blank=False, default="Sample Description")
    image_section_two_right = models.ImageField(upload_to='landingpage_images/', )
    image_section_two_header_right = models.CharField(max_length=100, blank=False, default="Sample Description")
    image_section_two_text_right = models.CharField(max_length=100, blank=False, default="Sample Description")
    # Section 3
    header_section_three = models.TextField(blank=False, default="Sample Description")
    text_section_three = models.TextField(blank=False, default="Sample Description")
    image_section_three_left = models.ImageField(upload_to='landingpage_images/', )
    image_section_three_right = models.ImageField(upload_to='landingpage_images/', )
    # Sponsor Images
    sponsors = models.ManyToManyField(sponsors, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        image_fields = [
            self.image_section_one,
            self.image_section_two_left,
            self.image_section_two_right,
            self.image_section_three_left,
            self.image_section_three_right
        ]

        for image_field in image_fields:
            if image_field:
                self.compress_image(image_field)

    def compress_image(self, image_field):
        img = Image.open(image_field.path)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        img.save(image_field.path, 'JPEG', quality=85, optimize=True)

    def delete(self, *args, **kwargs):
        # Delete image files when the instance is deleted
        image_fields = [
            self.image_section_one,
            self.image_section_two_left,
            self.image_section_two_right,
            self.image_section_three_left,
            self.image_section_three_right
        ]

        for image_field in image_fields:
            if image_field and os.path.isfile(image_field.path):
                os.remove(image_field.path)

        super().delete(*args, **kwargs)


class WhatsAppNumber(models.Model):
    name = models.CharField(max_length=100, blank=False, default="Contact Name")
    number = models.CharField(max_length=100, blank=False, default="62812345678", help_text="+62812345678 tanpa +")

    def __str__(self):
        return f"{self.name}: {self.number}"


class email_contact(models.Model):
    name = models.CharField(max_length=100, blank=False, default="Email Name")
    email = models.CharField(max_length=100, blank=False, default="admin@jakartaurologymedicalupdate.id",
                             help_text="contoh@gmail.com")

    def __str__(self):
        return f"{self.name}: {self.email}"


class about_us(models.Model):
    text_section_one = models.TextField(blank=False, default="Sample Description")
    header_section_two = models.CharField(max_length=100, blank=False, default="Sample Description")
    subheader_section_two_left = models.CharField(max_length=100, blank=False, default="Sample Description")
    text_section_two_left = models.TextField(blank=False, default="Sample Description")
    subheader_section_two_right = models.CharField(max_length=100, blank=False, default="Sample Description")
    text_section_two_right = models.TextField(blank=False, default="Sample Description")
    image_section_two = models.ImageField(upload_to='about_us_images/')
    whatsapp_numbers = models.ManyToManyField(WhatsAppNumber, blank=True)
    email_contact = models.ManyToManyField(email_contact, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        image_fields = [self.image_section_two]

        for image_field in image_fields:
            if image_field:
                self.compress_image(image_field)

    def compress_image(self, image_field):
        img = Image.open(image_field.path)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        img.save(image_field.path, 'JPEG', quality=85, optimize=True)


# Ticket General
class Seminar(models.Model):
    SEMINAR = 'Seminar'
    WORKSHOP = 'Workshop'
    CATEGORY_CHOICES = [
        (SEMINAR, 'Seminar'),
        (WORKSHOP, 'Workshop'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=False, default="Sample Description")
    image = models.ImageField(upload_to='seminar_images/', blank=True, null=True)
    date = models.DateTimeField()
    category = models.CharField(max_length=8, choices=CATEGORY_CHOICES, default=SEMINAR)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            self.compress_image()

    def compress_image(self):
        img = Image.open(self.image.path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(self.image.path, 'JPEG', quality=85, optimize=True)

    @property
    def total_available_seats(self):
        return sum(category.available_seats for category in self.ticket_categories.all())

    @property
    def total_remaining_seats(self):
        return sum(category.remaining_seats for category in self.ticket_categories.all())


class TicketCategory(models.Model):
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE, related_name='ticket_categories')
    name = models.CharField(max_length=100, default="umum")  # e.g., 'Student', 'Consultant', 'GP'
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    available_seats = models.IntegerField(default=1)
    reserved_seats = models.IntegerField(default=0)
    booked_seats = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.seminar.title} - {self.name}"

    @property
    def remaining_seats(self):
        return self.available_seats - (self.reserved_seats + self.booked_seats)

    def reserve_seats(self, quantity):
        if self.reserved_seats + quantity <= self.available_seats - self.booked_seats:
            self.reserved_seats += quantity
            self.save()
        else:
            raise ValueError("Cannot reserve more seats than available.")

    def release_seats(self, quantity):
        self.reserved_seats = max(self.reserved_seats - quantity, 0)
        self.save()


class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.PositiveIntegerField()
    used_count = models.PositiveIntegerField(default=0)

    def is_valid(self):
        now = timezone.now()
        return self.valid_from <= now <= self.valid_to and self.used_count < self.usage_limit

    def apply_discount(self, total):
        return total - (total * (self.discount_percentage / 100))

    def __str__(self):
        return self.code


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Cart for {self.user.username}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    ticket_category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} of {self.ticket_category.seminar.title} ({self.ticket_category.name})'

    def total_price(self):
        return self.quantity * self.ticket_category.price


@receiver(pre_save, sender=CartItem)
def track_initial_quantity(sender, instance, **kwargs):
    if instance.pk:
        instance._initial_quantity = CartItem.objects.get(pk=instance.pk).quantity
    else:
        instance._initial_quantity = 0


@receiver(post_save, sender=CartItem)
def reserve_seats_on_save(sender, instance, created, **kwargs):
    initial_quantity = getattr(instance, '_initial_quantity', 0)
    quantity_difference = instance.quantity - initial_quantity
    if quantity_difference > 0:
        instance.ticket_category.reserve_seats(quantity_difference)
    elif quantity_difference < 0:
        instance.ticket_category.release_seats(-quantity_difference)


@receiver(post_delete, sender=CartItem)
def release_seats_on_delete(sender, instance, **kwargs):
    instance.ticket_category.release_seats(instance.quantity)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    confirmation_date = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    @property
    def seminars(self):
        # Fetch seminars through OrderItems
        seminar_ids = self.orderitem_set.values_list('ticket_category__seminar_id', flat=True)
        return Seminar.objects.filter(id__in=seminar_ids).distinct()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    ticket_category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store the price at the time of purchase
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} of {self.ticket_category.seminar.title} ({self.ticket_category.name})'


class PaymentProof(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    proof = models.ImageField(upload_to='payment_proofs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    price_paid = models.DecimalField(max_digits=12, decimal_places=0, blank=True)

    def __str__(self):
        return f"Proof for {self.order.id}"
