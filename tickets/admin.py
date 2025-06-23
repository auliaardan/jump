from django.contrib import admin

from .models import Seminar, Order, PaymentProof, landing_page, about_us, seminars_page, workshops_page, Cart, CartItem, \
    WhatsAppNumber, email_contact, PaymentMethod, DiscountCode, WelcomingSpeech, TicketCategory, scicom_rules, qrcode, \
    Sponsor, ImageForPage, SciComSubmission

admin.site.register(TicketCategory)
admin.site.register(scicom_rules)
admin.site.register(Order)
admin.site.register(qrcode)
admin.site.register(PaymentProof)
admin.site.register(PaymentMethod)
admin.site.register(DiscountCode)
admin.site.register(ImageForPage)


@admin.register(SciComSubmission)
class SciComSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'submission_type',
        'abstract_title',
        'created_at',
        'is_accepted',
    )
    list_filter = ('submission_type', 'is_accepted')
    list_editable = ('is_accepted',)
    search_fields = ('user__nama_lengkap', 'abstract_title', 'abstract_authors')

    actions = ['mark_as_accepted']

    @admin.action(description='Mark selected abstracts as accepted')
    def mark_as_accepted(self, request, queryset):
        """
           For each SciComSubmission in the queryset that is not yet accepted,
            flip is_accepted=True and save() so the post_save signal will send the email.
        """
        accepted_count = 0
        # Only process those still False → avoid resending to already‐accepted rows
        for submission in queryset.filter(is_accepted=False):
            submission.is_accepted = True
            submission.save()  # triggers post_save signal → sends email
            accepted_count += 1
        # Let the admin know how many were updated
        self.message_user(
            request,
            f"✅ {accepted_count} abstract(s) marked as accepted and notification email sent."
        )


class TicketCategoryInline(admin.TabularInline):
    model = TicketCategory
    extra = 1


@admin.register(Seminar)
class SeminarAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'end_date', 'location', 'category')
    inlines = [TicketCategoryInline]


class WhatsAppNumberInline(admin.TabularInline):
    model = about_us.whatsapp_numbers.through
    extra = 1


class PhoneNumberInline(admin.TabularInline):
    model = about_us.email_contact.through
    extra = 1


class WelcomingSpeechesInline(admin.TabularInline):
    model = landing_page.welcoming.through
    extra = 1


@admin.register(WelcomingSpeech)
class WelcomingSpeechesAdmin(admin.ModelAdmin):
    list_display = ('name', 'title')


@admin.register(about_us)
class AboutUsAdmin(admin.ModelAdmin):
    inlines = [WhatsAppNumberInline, PhoneNumberInline]


class SponsorInline(admin.TabularInline):
    model = landing_page.sponsor.through
    extra = 1


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(landing_page)
class LandingPageAdmin(admin.ModelAdmin):
    inlines = [WelcomingSpeechesInline, SponsorInline]


@admin.register(WhatsAppNumber)
class WhatsAppNumberAdmin(admin.ModelAdmin):
    list_display = ['name', 'number']


@admin.register(email_contact)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']


admin.site.register(seminars_page)
admin.site.register(workshops_page)
admin.site.register(Cart)
admin.site.register(CartItem)
