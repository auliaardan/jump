import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from openpyxl.workbook import Workbook

from .forms import PaymentProofForm
from .forms import UserRegisterForm, AddToCartForm
from .models import paymentmethod, Seminar, Order, landing_page, Cart, CartItem, about_us, seminars_page, \
    workshops_page, DiscountCode


class WorkshopView(ListView):
    model = workshops_page
    template_name = 'Workshops.html'
    context_object_name = 'workshops'

    def get_queryset(self):
        return workshops_page.objects.last()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')

        if search_query:
            seminars = Seminar.objects.filter(title__icontains=search_query).order_by('id')
        else:
            seminars = Seminar.objects.filter(category=Seminar.WORKSHOP).order_by('id')

        paginator = Paginator(seminars, 4)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        num_placeholders = 4 - len(page_obj) if len(page_obj) < 4 else 0

        context['seminar_list'] = page_obj
        context['num_placeholders'] = num_placeholders
        context['has_next'] = page_obj.has_next()
        context['has_previous'] = page_obj.has_previous()
        context['search_query'] = search_query
        return context


class SeminarsView(ListView):
    model = seminars_page
    template_name = 'Seminars.html'
    context_object_name = 'seminars'

    def get_queryset(self):
        return seminars_page.objects.last()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')

        if search_query:
            seminars = Seminar.objects.filter(title__icontains=search_query).order_by('id')
        else:
            seminars = Seminar.objects.filter(category=Seminar.SEMINAR).order_by('id')

        paginator = Paginator(seminars, 4)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Calculate the number of placeholders needed to maintain the layout
        num_placeholders = 4 - len(page_obj) if len(page_obj) < 4 else 0

        context['seminar_list'] = page_obj
        context['num_placeholders'] = num_placeholders
        context['has_next'] = page_obj.has_next()
        context['has_previous'] = page_obj.has_previous()
        context['search_query'] = search_query
        return context


class baseView(ListView):
    model = landing_page
    template_name = 'index.html'
    context_object_name = "landing"

    def get_queryset(self):
        return landing_page.objects.last()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')

        if search_query:
            seminars = Seminar.objects.filter(title__icontains=search_query).order_by('id')
        else:
            seminars = Seminar.objects.all().order_by('id')

        paginator = Paginator(seminars, 4)  # Show 4 seminars per page
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Calculate the number of placeholders needed to maintain the layout
        num_placeholders = 4 - len(page_obj) if len(page_obj) < 4 else 0

        context['seminar_list'] = page_obj
        context['num_placeholders'] = num_placeholders
        context['has_next'] = page_obj.has_next()
        context['has_previous'] = page_obj.has_previous()
        context['search_query'] = search_query
        return context


class about_us_view(ListView):
    model = about_us
    template_name = 'about_us.html'
    context_object_name = "about_us"

    def get_queryset(self):
        return about_us.objects.last()


def order_confirmed(request):
    return render(request, 'tickets/order_confirmed.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'tickets/register.html', {'form': form})


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        total = sum(item.total_price() for item in cart.cartitem_set.all())
        payment_method = paymentmethod.objects.last()
        form = PaymentProofForm()
        return render(request, 'tickets/checkout.html',
                      {'cart': cart, 'total': total, 'form': form, 'payment_method': payment_method})

    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        total_str = request.POST.get('final_total', sum(item.total_price() for item in cart.cartitem_set.all()))
        total = float(total_str.replace(',', '.'))

        order = Order.objects.create(user=request.user)
        order.seminars.set([item.seminar for item in cart.cartitem_set.all()])

        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            proof = form.save(commit=False)
            proof.order = order
            proof.save()

            # URL of the hosted image
            image_url = 'https://awsimages.detik.net.id/community/media/visual/2022/08/05/kop-surat-5.jpeg?w=685'

            email_subject = 'Your Order Confirmation'
            email_body = render_to_string('tickets/emails/payment_received.html', {
                'user': request.user,
                'order': order,
                'total': total,
                'cart': cart,
                'image_url': image_url,
            })
            email = EmailMessage(
                email_subject,
                email_body,
                'admin@inapro.org',
                [request.user.email],
            )
            email.content_subtype = 'html'
            email.send()

            cart.cartitem_set.all().delete()

            return redirect('order_confirmed')

        return render(request, 'tickets/checkout.html', {'cart': cart, 'total': total, 'form': form})


def apply_discount(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        discount_code = data.get('discount_code', '')
        cart = get_object_or_404(Cart, user=request.user)
        total = sum(item.total_price() for item in cart.cartitem_set.all())

        try:
            discount = DiscountCode.objects.get(code=discount_code)
            if discount.is_valid():
                new_total = discount.apply_discount(total)
                formatted_total = "Rp " + f"{int(new_total):,}".replace(",", ".")
                return JsonResponse({'success': True, 'new_total': formatted_total})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid or expired discount code.'})
        except DiscountCode.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid discount code.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})


@staff_member_required
def admin_dashboard(request):
    orders = Order.objects.all().order_by('-created_at')
    seminars = Seminar.objects.all().order_by('date')
    return render(request, 'tickets/admin_dashboard.html', {'orders': orders, 'seminars': seminars})



@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'orders': orders})


@staff_member_required
def admin_dashboard_view(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_dashboard.html', {'orders': orders})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tickets/order_history.html', {'orders': orders})


class SeminarDetailView(DetailView):
    model = Seminar
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'seminar'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seminar = self.get_object()
        context['form'] = AddToCartForm(seminar=seminar)

        search_query = self.request.GET.get('search', '')

        if search_query:
            seminars = Seminar.objects.filter(title__icontains=search_query).order_by('id')
        else:
            seminars = Seminar.objects.all().order_by('id')

        paginator = Paginator(seminars, 4)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Calculate the number of placeholders needed to maintain the layout
        num_placeholders = 4 - len(page_obj) if len(page_obj) < 4 else 0

        context['seminar_list'] = page_obj
        context['num_placeholders'] = num_placeholders
        context['has_next'] = page_obj.has_next()
        context['has_previous'] = page_obj.has_previous()
        context['search_query'] = search_query
        return context

    def post(self, request, *args, **kwargs):
        seminar = self.get_object()
        form = AddToCartForm(request.POST, seminar=seminar)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, seminar=seminar)
            if created:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            if cart_item.quantity > seminar.available_seats:
                cart_item.quantity = seminar.available_seats
            cart_item.save()
            return redirect('cart_detail')
        return self.get(request, *args, **kwargs)


@login_required
def cart_item_count(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    item_count = cart.cartitem_set.count()
    return JsonResponse({'item_count': item_count})


class CartDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        is_empty = not cart.cartitem_set.exists()
        return render(request, 'tickets/cart_detail.html', {'cart': cart, 'is_empty': is_empty})


class RemoveFromCartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart_item = get_object_or_404(CartItem, id=kwargs['item_id'])
        cart_item.delete()  # This will trigger the post_delete signal to release seats
        return redirect('cart_detail')


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        seminar = get_object_or_404(Seminar, id=kwargs['seminar_id'])
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, seminar=seminar)

        quantity = int(request.POST.get('quantity', 1))

        if created:
            cart_item.quantity = quantity  # Set initial quantity
        else:
            cart_item.quantity += quantity  # Increment quantity

        if seminar.remaining_seats < cart_item.quantity:
            return JsonResponse({'success': False, 'message': 'Not enough remaining seats'})

        cart_item.save()

        response = {
            'success': True,
            'message': 'Added to cart successfully!',
            'quantity': cart_item.quantity,
            'remaining_seats': seminar.remaining_seats,
            'item_count': cart.cartitem_set.count()
        }
        return JsonResponse(response)


@staff_member_required
@require_POST
def confirm_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_confirmed = True
    order.confirmation_date = timezone.now()
    order.transaction_id = request.POST.get('transaction_id')
    order.save()

    # Confirm seats for each seminar in the order
    for seminar in order.seminars.all():
        cart_item = CartItem.objects.filter(cart__user=order.user, seminar=seminar).first()
        if cart_item:
            seminar.confirm_seats(cart_item.quantity)

    # Send confirmation email
    email_subject = 'Order Confirmation'
    email_body = render_to_string('tickets/emails/order_confirmed.html', {'user': order.user})
    email = EmailMessage(
        email_subject,
        email_body,
        'admin@inapro.org',
        [order.user.email],
    )
    email.content_subtype = 'html'

    try:
        email.send()
    except Exception as e:
        # Handle email sending error
        print(f"Error sending email: {e}")

    return redirect('admin_dashboard')


@staff_member_required
def export_orders_view(request):
    # Create a workbook and activate the worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"

    # Write the header
    headers = ['User', 'Order ID', 'Created At', 'Confirmed', 'Confirmation Date', 'Seminars', 'Total Price']
    ws.append(headers)

    # Write the data
    orders = Order.objects.all()
    for order in orders:
        # Remove timezone info
        created_at_naive = order.created_at.replace(tzinfo=None) if order.created_at else None
        confirmation_date_naive = order.confirmation_date.replace(tzinfo=None) if order.confirmation_date else None

        # Get seminars and total price
        seminar_titles = [seminar.title for seminar in order.seminars.all()]
        seminars_str = ", ".join(seminar_titles)

        # Calculate total price considering any discounts
        total_price = sum(cart_item.total_price() for cart_item in
                          CartItem.objects.filter(cart__user=order.user, seminar__in=order.seminars.all()))
        discount_code = order.user.profile.discount_code if hasattr(order.user.profile, 'discount_code') else None
        if discount_code and discount_code.is_valid():
            total_price = discount_code.apply_discount(total_price)

        # Write the row
        ws.append([
            order.user.username,
            order.id,
            created_at_naive,
            'Yes' if order.is_confirmed else 'No',
            confirmation_date_naive,
            seminars_str,
            total_price
        ])

    # Create an HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="orders.xlsx"'
    wb.save(response)

    return response