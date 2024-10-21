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
from django.db.models.signals import post_delete
from .models import release_seats_on_delete

from .forms import PaymentProofForm
from .forms import UserRegisterForm, AddToCartForm
from .models import PaymentMethod, Seminar, Order, landing_page, Cart, CartItem, about_us, seminars_page, \
    workshops_page, DiscountCode, PaymentProof


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
        payment_method = PaymentMethod.objects.last()
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
            proof.price_paid = int(total)
            proof.save()

            email_subject = 'Your Order Confirmation'
            email_body = render_to_string('tickets/emails/payment_received.html', {
                'user': request.user,
                'order': order,
                'total': int(total),
                'cart': cart,
            })
            email = EmailMessage(
                email_subject,
                email_body,
                'jakartau@jakartaurologymedicalupdate.id',
                [request.user.email],
            )
            email.content_subtype = 'html'
            print("Email Sent")
            email.send()

            if request.POST.get('discount_code_form') == "True":
                code = request.POST.get('discount_code_name')
                discount_code = get_object_or_404(DiscountCode, code=code)
                if discount_code.is_valid():
                    discount_code.used_count += 1
                    discount_code.save()

            for item in cart.cartitem_set.all():
                seminar = item.seminar
                seminar.booked += item.quantity
                seminar.reserved_seats -= item.quantity
                seminar.save()

            # Temporarily disconnect the 'release_seats_on_delete' signal
            post_delete.disconnect(release_seats_on_delete, sender=CartItem)

            # Delete cart items
            cart.cartitem_set.all().delete()

            # Reconnect the signal
            post_delete.connect(release_seats_on_delete, sender=CartItem)

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


class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'not_authenticated'})

        seminar = get_object_or_404(Seminar, id=kwargs['seminar_id'])
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, seminar=seminar)

        quantity = int(request.POST.get('quantity', 1))

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        if seminar.remaining_seats < quantity:
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

    email_subject = 'Order Confirmation'
    email_body = render_to_string('tickets/emails/order_confirmed.html', {'user': order.user})
    email = EmailMessage(
        email_subject,
        email_body,
        'jakartau@jakartaurologymedicalupdate.id',
        [order.user.email],
    )
    email.content_subtype = 'html'

    try:
        email.send()
        print("Email Sent")
    except Exception as e:
        print(f"Error sending email: {e}")

    return redirect('admin_dashboard')


@staff_member_required
def export_orders_view(request):
    # Create a workbook and activate the worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"

    # Write the header
    headers = ['User', 'Name', 'Phone Number', 'Order ID', 'Created At', 'Confirmed', 'Confirmation Date', 'Seminars',
               'Total Price']
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

        # Calculate total price from PaymentProof
        payment_proof = PaymentProof.objects.filter(order=order).first()
        price_paid = payment_proof.price_paid if payment_proof else 0

        # Get user details
        user = order.user
        full_name = f"{user.first_name} {user.last_name}"
        phone_number = user.phone_number

        # Write the row
        ws.append([
            user.username,
            full_name,
            phone_number,
            order.id,
            created_at_naive,
            'Yes' if order.is_confirmed else 'No',
            confirmation_date_naive,
            seminars_str,
            price_paid
        ])

    # Create an HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="order_report.xlsx"'
    wb.save(response)

    return response
