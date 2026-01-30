import os
# models.py
import uuid
from io import BytesIO
from django.urls import reverse

# pip install qrcode[pil]
import qrcode as qr_lib
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from jump_project import settings
from jump_project.settings import AUTH_USER_MODEL as User


class ImageForPage(models.Model):
    WORKSHOP = 'Workshop'
    SEMINAR = 'Seminar'
    SCICOM = 'Scicom'
    CATEGORY_CHOICES = [
        (WORKSHOP, 'Workshop'),
        (SEMINAR, 'Seminar'),
        (SCICOM, 'Scicom'),
    ]
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default=SEMINAR)
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return f"{self.image}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        image_fields = [
            self.image,
        ]

        for image_field in image_fields:
            if image_field:
                self.compress_image(image_field)

    def compress_image(self, image_field):
        img = Image.open(image_field.path)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        img.save(image_field.path, 'JPEG', quality=85, optimize=True)


class scicom_rules(models.Model):
    rule_name = models.TextField(blank=False, default="Sample Description")
    rule_description = models.TextField(blank=True, null=True, default="Sample Description")
    pdf_file = models.FileField(upload_to='scicom_pdfs/', blank=True, null=True)

    def __str__(self):
        return f"{self.rule_name}"

    def get_description_lines(self):
        if self.rule_description:
            return self.rule_description.splitlines()
        else:
            return []


@receiver(post_delete, sender=scicom_rules)
def delete_pdf_file(sender, instance, **kwargs):
    if instance.pdf_file:
        # Check if the file exists
        if os.path.isfile(instance.pdf_file.path):
            os.remove(instance.pdf_file.path)


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


class seminars_page(models.Model):
    text_section_one = models.TextField(blank=False, default="Sample Description")
    text_section_two = models.TextField(blank=False, default="Sample Description")


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


@receiver(post_delete, sender=WelcomingSpeech)
def delete_welcoming_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


class Sponsor(models.Model):
    LARGE = 'Large'
    MEDIUM = 'Medium'
    SMALL = 'Small'
    CATEGORY_CHOICES = [
        (LARGE, 'Large'),
        (MEDIUM, 'Medium'),
        (SMALL, 'Small'),
    ]

    name = models.TextField(blank=False, default="Sample Description")
    image = models.ImageField(upload_to='sponsor_images/', )
    banner = models.ImageField(upload_to='sponsor_banner_images/', blank=True, null=True)
    category = models.CharField(max_length=8, choices=CATEGORY_CHOICES, default=SMALL)
    youtube_video_id = models.CharField(max_length=20, blank=True, null=True,
                                        help_text="YouTube video ID for the sponsor")

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        image_fields = [
            self.image,
            self.banner,
        ]

        for image_field in image_fields:
            if image_field:
                self.compress_image(image_field)

    def compress_image(self, image_field):
        try:
            img = Image.open(image_field.path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(image_field.path, 'JPEG', quality=85, optimize=True)
        except IOError:
            pass


@receiver(post_delete, sender=Sponsor)
def delete_sponsor_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


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
    sponsor = models.ManyToManyField(Sponsor, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        image_fields = [
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

    # Up to 5 images allowed
    image_section_two_1 = models.ImageField(upload_to='about_us_images/', blank=True, null=True)
    image_section_two_2 = models.ImageField(upload_to='about_us_images/', blank=True, null=True)
    image_section_two_3 = models.ImageField(upload_to='about_us_images/', blank=True, null=True)
    image_section_two_4 = models.ImageField(upload_to='about_us_images/', blank=True, null=True)
    image_section_two_5 = models.ImageField(upload_to='about_us_images/', blank=True, null=True)

    whatsapp_numbers = models.ManyToManyField(WhatsAppNumber, blank=True)
    email_contact = models.ManyToManyField(email_contact, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        image_fields = [
            self.image_section_two_1,
            self.image_section_two_2,
            self.image_section_two_3,
            self.image_section_two_4,
            self.image_section_two_5,
        ]

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
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True, default="RSCM")
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


class SciComSubmission(models.Model):
    # Submission Types
    ABSTRACT = 'abstract'
    VIDEO = 'video'
    FLYER = 'flyer'
    SUBMISSION_TYPE_CHOICES = [
        (ABSTRACT, 'Paper Abstract'),
        (VIDEO, 'Educative Video'),
        (FLYER, 'Educative Flyer'),
    ]

    # Paper Types (only used if submission_type = ABSTRACT)
    CASE_REPORT = 'Case Report'
    PRIMARY_STUDY = 'Primary Study'
    SECONDARY_STUDY = 'Secondary Study'
    SYSTEMATIC_REVIEW = 'Systematic Review'
    META_ANALYSIS = 'Meta Analysis'
    PAPER_TYPE_CHOICES = [
        (CASE_REPORT, 'Case Report'),
        (PRIMARY_STUDY, 'Primary Study'),
        (SECONDARY_STUDY, 'Secondary Study'),
        (SYSTEMATIC_REVIEW, 'Systematic Review'),
        (META_ANALYSIS, 'Meta Analysis'),
    ]
    UROLOGIST = 'Urologist'
    RESIDENT = 'Resident'
    GENERAL_PRACTITIONER = 'General Practitioner'
    MEDICAL_STUDENT = 'Medical Student'
    OCCUPATION_CHOICES = [
        (UROLOGIST, 'Urologist'),
        (RESIDENT, 'Resident'),
        (GENERAL_PRACTITIONER, 'General Practitioner'),
        (MEDICAL_STUDENT, 'Medical Student'),
    ]

    # We still store "address" if you want that separate from CustomUser
    address = models.TextField(blank=False, null=False, default="Jakarta, Indonesia")

    occupation = models.CharField(
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=UROLOGIST
    )

    # Link to your CustomUser
    user = models.ForeignKey(
        User,  # "yourapp.CustomUser" also works
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    # The "type" of this submission (Abstract, Video, or Flyer)
    submission_type = models.CharField(
        max_length=10,
        choices=SUBMISSION_TYPE_CHOICES,
        default=ABSTRACT
    )

    # For Abstract
    abstract_title = models.CharField(max_length=250, blank=True, null=True)
    paper_type = models.CharField(
        max_length=50,
        choices=PAPER_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text="Only valid for Abstract submission"
    )
    abstract_authors = models.TextField(
        blank=True,
        null=True,
        help_text="List authors separated by commas",

    )
    abstract_text = models.TextField(blank=True, null=True)
    link_abstract = models.URLField(
        blank=True,
        null=True,
        help_text="Link to the full abstract or PDF (Google Drive, etc.)"
    )

    # For Educative Video
    video_title = models.CharField(max_length=250, blank=True, null=True)
    video_authors = models.TextField(
        blank=True,
        null=True,
        help_text="List authors separated by commas"
    )
    link_video = models.URLField(blank=True, null=True)

    # For Educative Flyer
    flyer_title = models.CharField(max_length=250, blank=True, null=True)
    flyer_authors = models.TextField(
        blank=True,
        null=True,
        help_text="List authors separated by commas"
    )
    link_flyer = models.URLField(blank=True, null=True)

    is_accepted = models.BooleanField(
        default=False,
        help_text="Tick to mark this abstract as accepted."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # --------------------------------
    # PROPERTIES to pull from user
    # --------------------------------
    @property
    def name(self):
        """Full name from the CustomUser (nama_lengkap)."""
        return self.user.nama_lengkap

    @property
    def affiliation(self):
        """Institution from the CustomUser."""
        return self.user.institution

    @property
    def email(self):
        """Email from the CustomUser (AbstractUser email field)."""
        return self.user.email

    @property
    def phone(self):
        """Phone from the CustomUser (Nomor_telpon)."""
        return self.user.Nomor_telpon

    # If you need to check if user "already registered" for a "Seminar"
    # We'll assume you have an Order model referencing TicketCategory -> Seminar
    @property
    def already_registered(self):
        """
        Checks if this user has a confirmed order (is_confirmed=True)
        for a Seminar (category='Seminar').
        """
        return Order.objects.filter(
            user=self.user,
            is_confirmed=True,
            orderitem__ticket_category__seminar__category='Seminar'
        ).exists()

    def __str__(self):
        # e.g. "abstract by John Doe" or "flyer by Jane"
        return f"{self.submission_type} by {self.name}"

    def clean(self):
        """Optional: Validation logic for required fields based on submission_type."""
        if self.submission_type == self.ABSTRACT:
            # Enforce required abstract fields
            required_fields = ['abstract_title', 'paper_type', 'abstract_authors', 'abstract_text']
            for field_name in required_fields:
                value = getattr(self, field_name)
                if not value:
                    raise ValidationError(
                        f"{field_name.replace('_', ' ').title()} is required for Abstract submissions.")

            # Check only the allowed paper types
            valid_paper_types = [choice[0] for choice in self.PAPER_TYPE_CHOICES]
            if self.paper_type and self.paper_type not in valid_paper_types:
                raise ValidationError("Invalid paper_type provided for Abstract submission.")

        elif self.submission_type == self.VIDEO:
            required_fields = ['video_title', 'video_authors', 'link_video']
            for field_name in required_fields:
                value = getattr(self, field_name)
                if not value:
                    raise ValidationError(f"{field_name.replace('_', ' ').title()} is required for Video submissions.")

        elif self.submission_type == self.FLYER:
            required_fields = ['flyer_title', 'flyer_authors', 'link_flyer']
            for field_name in required_fields:
                value = getattr(self, field_name)
                if not value:
                    raise ValidationError(f"{field_name.replace('_', ' ').title()} is required for Flyer submissions.")

    def save(self, *args, **kwargs):
        # run model validation
        self.clean()
        super().save(*args, **kwargs)


class AcceptedAbstractSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    abstract = models.ForeignKey(
        SciComSubmission,
        on_delete=models.CASCADE,
        limit_choices_to={'submission_type': SciComSubmission.ABSTRACT}
    )
    ppt_link = models.URLField(help_text="Link to the PowerPoint presentation")
    poster_link = models.URLField(help_text="Link to the E-Poster")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Accepted Abstract #{self.id} by {self.user.nama_lengkap}"


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='tickets')
    order_item = models.ForeignKey('OrderItem', on_delete=models.CASCADE, related_name='tickets')

    attendee_name = models.CharField(max_length=255, blank=True, null=True)  # optional
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(blank=True, null=True)

    qr_image = models.ImageField(upload_to="tickets/qr/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def mark_checked_in(self):
        if not self.checked_in:
            self.checked_in = True
            self.checked_in_at = timezone.now()
            self.save(update_fields=["checked_in", "checked_in_at"])

    def get_absolute_url(self):
        return reverse("ticket_booked_detail", kwargs={"ticket_id": self.id})

    def generate_qr(self, absolute_ticket_url: str):
        qr = qr_lib.QRCode(box_size=10, border=3)
        qr.add_data(absolute_ticket_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f"ticket-{self.id}.png"
        self.qr_image.save(filename, ContentFile(buffer.getvalue()), save=False)
