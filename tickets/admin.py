from django.contrib import admin

from .models import Seminar, Order, PaymentProof, landing_page, about_us, seminars_page, workshops_page, Cart, CartItem, \
    WhatsAppNumber, email_contact, PaymentMethod, DiscountCode, WelcomingSpeech, TicketCategory, scicom_rules, qrcode, \
    Sponsor, ImageForPage

admin.site.register(TicketCategory)
admin.site.register(scicom_rules)
admin.site.register(Order)
admin.site.register(qrcode)
admin.site.register(PaymentProof)
admin.site.register(PaymentMethod)
admin.site.register(DiscountCode)
admin.site.register(ImageForPage)


class TicketCategoryInline(admin.TabularInline):
    model = TicketCategory
    extra = 1


@admin.register(Seminar)
class SeminarAdmin(admin.ModelAdmin):
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
    list_display = ('name', )

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
