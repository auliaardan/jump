from django.contrib import admin
from .models import Seminar, Order, PaymentProof, landing_page, about_us, seminars_page, workshops_page, Cart, CartItem

admin.site.register(Seminar)
admin.site.register(Order)
admin.site.register(PaymentProof)
admin.site.register(landing_page)
admin.site.register(about_us)
admin.site.register(seminars_page)
admin.site.register(workshops_page)
admin.site.register(Cart)
admin.site.register(CartItem)

