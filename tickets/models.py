from PIL import Image
from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from jump_project.settings import AUTH_USER_MODEL as User


class paymentmethod(models.Model):
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


class landing_page(models.Model):
    header_section_one = models.TextField(blank=False, default="Sample Description")
    text_section_one = models.TextField(blank=False, default="Sample Description")
    image_section_one = models.ImageField(upload_to='landingpage_images/', )
    header_section_two = models.CharField(max_length=100, blank=False, default="Sample Description")
    text_section_two = models.TextField(blank=False, default="Sample Description")
    image_section_two_left = models.ImageField(upload_to='landingpage_images/', )
    image_section_two_header_left = models.CharField(max_length=100, blank=False, default="Sample Description")
    image_section_two_text_left = models.CharField(max_length=100, blank=False, default="Sample Description")
    image_section_two_right = models.ImageField(upload_to='landingpage_images/', )
    image_section_two_header_right = models.CharField(max_length=100, blank=False, default="Sample Description")
    image_section_two_text_right = models.CharField(max_length=100, blank=False, default="Sample Description")
    header_section_three = models.TextField(blank=False, default="Sample Description")
    text_section_three = models.TextField(blank=False, default="Sample Description")
    image_section_three_left = models.ImageField(upload_to='landingpage_images/', )
    image_section_three_right = models.ImageField(upload_to='landingpage_images/', )

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


class WhatsAppNumber(models.Model):
    name = models.CharField(max_length=100, blank=False, default="Contact Name")
    number = models.CharField(max_length=100, blank=False, default="62812345678", help_text="+62812345678 tanpa +")

    def __str__(self):
        return f"{self.name}: {self.number}"


class PhoneNumber(models.Model):
    name = models.CharField(max_length=100, blank=False, default="Contact Name")
    number = models.CharField(max_length=100, blank=False, default="+62812345678", help_text="+62812345678")

    def __str__(self):
        return f"{self.name}: {self.number}"


class about_us(models.Model):
    text_section_one = models.TextField(blank=False, default="Sample Description")
    header_section_two = models.CharField(max_length=100, blank=False, default="Sample Description")
    subheader_section_two_left = models.CharField(max_length=100, blank=False, default="Sample Description")
    text_section_two_left = models.TextField(blank=False, default="Sample Description")
    subheader_section_two_right = models.CharField(max_length=100, blank=False, default="Sample Description")
    text_section_two_right = models.TextField(blank=False, default="Sample Description")
    image_section_two = models.ImageField(upload_to='about_us_images/')
    whatsapp_numbers = models.ManyToManyField(WhatsAppNumber, blank=True)
    phone_numbers = models.ManyToManyField(PhoneNumber, blank=True)

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
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    available_seats = models.IntegerField(blank=False, default=1)
    reserved_seats = models.IntegerField(default=0)

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
    def remaining_seats(self):
        return self.available_seats - self.reserved_seats

    def reserve_seats(self, quantity):
        if self.remaining_seats >= quantity:
            self.reserved_seats += quantity
            self.save()
            return True
        return False

    def release_seats(self, quantity):
        if self.reserved_seats >= quantity:
            self.reserved_seats -= quantity
            self.save()
            return True
        return False

    def confirm_seats(self, quantity):
        if self.reserved_seats >= quantity:
            self.available_seats -= quantity
            self.reserved_seats -= quantity
            self.save()
            return True
        return False


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Cart for {self.User.username}'


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


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} of {self.seminar.title}'

    def total_price(self):
        return self.quantity * self.seminar.price


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
        instance.seminar.reserve_seats(quantity_difference)
    elif quantity_difference < 0:
        instance.seminar.release_seats(-quantity_difference)


@receiver(post_delete, sender=CartItem)
def release_seats_on_delete(sender, instance, **kwargs):
    instance.seminar.release_seats(instance.quantity)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seminars = models.ManyToManyField(Seminar)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    confirmation_date = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {', '.join([seminar.title for seminar in self.seminars.all()])}"


@receiver(post_save, sender=Order)
def confirm_order(sender, instance, **kwargs):
    if instance.is_confirmed:
        for seminar in instance.seminars.all():
            cart_item = CartItem.objects.filter(cart__user=instance.user, seminar=seminar).first()
            if cart_item:
                seminar.confirm_seats(cart_item.quantity)


class PaymentProof(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    proof = models.ImageField(upload_to='payment_proofs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proof for {self.order.id}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
