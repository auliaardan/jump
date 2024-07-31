from PIL import Image
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


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


class about_us(models.Model):
    text_section_one = models.TextField(blank=False, default="Sample Description")
    header_section_two = models.CharField(max_length=100, blank=False, default="Sample Description")
    subheader_section_two_left = models.CharField(max_length=100, blank=False, default="Sample Description")
    text_section_two_left = models.TextField(blank=False, default="Sample Description")
    subheader_section_two_right = models.CharField(max_length=100, blank=False, default="Sample Description")
    text_section_two_right = models.TextField(blank=False, default="Sample Description")
    image_section_two = models.ImageField(upload_to='about_us_images/', )
    whatsapp_number = models.CharField(max_length=100, blank=False, default="62812345678  tanpa +",
                                       help_text="+62812345678 tanpa +")
    phone_number = models.CharField(max_length=100, blank=False, default="+62812345678", help_text="+62812345678")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        image_fields = [
            self.image_section_two,
        ]

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
        reserved_seats = sum(item.quantity for item in self.cartitem_set.all())
        return self.available_seats - reserved_seats


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Cart for {self.user.username}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} of {self.seminar.title}'

    def total_price(self):
        return self.quantity * self.seminar.price


@receiver(post_save, sender=CartItem)
@receiver(post_delete, sender=CartItem)
def update_remaining_seats(sender, instance, **kwargs):
    instance.seminar.save()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    confirmation_date = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.seminar.title}"


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
