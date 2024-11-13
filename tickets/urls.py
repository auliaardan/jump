from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import SeminarDetailView, CartDetailView, RemoveFromCartView, AddToCartView, about_us_view, SeminarsView, \
    WorkshopView, CheckoutView, apply_discount, cart_item_count, ScicomView

urlpatterns = [
                  path('', views.baseView.as_view(), name='seminar_list'),
                  path('cart_item_count/', cart_item_count, name='cart_item_count'),
                  path('seminar/<int:pk>/', SeminarDetailView.as_view(), name='seminar_detail'),
                  path('seminars/', SeminarsView.as_view(), name='seminar_page'),
                  path('workshops/', WorkshopView.as_view(), name='workshop_page'),
                  path('scientific_competition/', ScicomView.as_view(), name='scicom_page'),
                  path('cart/', CartDetailView.as_view(), name='cart_detail'),
                  path('about_us/', about_us_view.as_view(), name='about_us'),
                  path('remove_from_cart/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
                  path('add_to_cart/<int:seminar_id>/', AddToCartView.as_view(), name='add_to_cart'),
                  path('checkout/', CheckoutView.as_view(), name='checkout'),
                  path('apply_discount/', apply_discount, name='apply_discount'),
                  path('order_confirmed/', views.order_confirmed, name='order_confirmed'),
                  path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
                  path('confirm_order/<int:order_id>/', views.confirm_order_view, name='confirm_order'),
                  path('export_orders/', views.export_orders_view, name='export_orders'),
                  path('profile/', views.profile_view, name='profile'),
                  path('order_history/', views.order_history, name='order_history'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
