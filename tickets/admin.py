from django.contrib import admin
from .models import Seminar, Order, PaymentProof

admin.site.register(Seminar)
admin.site.register(Order)
admin.site.register(PaymentProof)
