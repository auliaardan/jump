from django.contrib import admin

from .models import Seminar, Order, PaymentProof, landing_page, about_us, seminars_page, workshops_page, Cart, CartItem, \
    WhatsAppNumber, email_contact, PaymentMethod, DiscountCode

admin.site.register(Seminar)
admin.site.register(Order)
admin.site.register(PaymentProof)
admin.site.register(landing_page)
admin.site.register(PaymentMethod)
admin.site.register(DiscountCode)


class WhatsAppNumberInline(admin.TabularInline):
    model = about_us.whatsapp_numbers.through
    extra = 1


class PhoneNumberInline(admin.TabularInline):
    model = about_us.email_contact.through
    extra = 1


@admin.register(about_us)
class AboutUsAdmin(admin.ModelAdmin):
    inlines = [WhatsAppNumberInline, PhoneNumberInline]


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
