from django.contrib import admin
from .models import Seminar, Order, PaymentProof, landing_page

admin.site.register(Seminar)
admin.site.register(Order)
admin.site.register(PaymentProof)
admin.site.register(landing_page)