from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.baseView.as_view(), name='seminar_list'),
    path('order/<int:seminar_id>/', views.create_order, name='create_order'),
    path('upload_proof/<int:order_id>/', views.upload_proof, name='upload_proof'),
    path('order_confirmed/', views.order_confirmed, name='order_confirmed'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('confirm_order/<int:order_id>/', views.confirm_order, name='confirm_order'),
    path('profile/', views.profile, name='profile'),
    path('order_history/', views.order_history, name='order_history'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)