import json
import datetime
import re

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from openpyxl.workbook import Workbook

from .forms import PaymentProofForm, UserRegisterForm, SciComSubmissionForm
from .models import PaymentMethod, Seminar, Order, landing_page, Cart, CartItem, about_us, seminars_page, \
    workshops_page, DiscountCode, PaymentProof, scicom_rules, qrcode, ImageForPage, Sponsor, SciComSubmission
from .models import TicketCategory, OrderItem


@login_required
def create_submission(request):
    if request.method == 'POST':
        form = SciComSubmissionForm(request.POST)
        if form.is_valid():
            new_submission = form.save(commit=False)
            # Link the user from request
            new_submission.user = request.user
            new_submission.save()
            email_subject = 'Your Submission Confirmation'
            email_body = render_to_string('tickets/emails/submission_confirmed.html', {
                'name': new_submission.user.nama_lengkap,
                'type': new_submission.get_submission_type_display(),
            })
            email = EmailMessage(
                email_subject,
                email_body,
                'admin@jump2025.com',
                [new_submission.user.email],
            )
            email.content_subtype = 'html'
            email.send()
            return redirect('seminar_list')
    else:
        # Suppose we want to default to "abstract"
        form = SciComSubmissionForm(initial={'submission_type': 'abstract'})
        form.instance.user = request.user

    return render(request, 'tickets/create_submission.html', {'form': form})


class SponsorsView(ListView):
    model = Sponsor
    template_name = 'Sponsors.html'
    context_object_name = 'sponsors'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sponsors = Sponsor.objects.all()
        platinum_sponsors = sponsors.filter(category='Large')
        gold_sponsors = sponsors.filter(category='Medium')
        silver_sponsors = sponsors.filter(category='Small')

        context['sponsors'] = sponsors
        context['platinum_sponsors'] = platinum_sponsors
        context['gold_sponsors'] = gold_sponsors
        context['silver_sponsors'] = silver_sponsors
        return context


class ScicomView(ListView):
    model = scicom_rules
    template_name = 'scicom.html'
    context_object_name = 'scicom_rules'

    def get_queryset(self):
        return scicom_rules.objects.all()

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

        qrcode_obj = qrcode.objects.last()
        images = ImageForPage.objects.filter(category=ImageForPage.SCICOM)

        context['images'] = images
        context['qrcode'] = qrcode_obj
        context['seminar_list'] = page_obj
        context['num_placeholders'] = num_placeholders
        context['has_next'] = page_obj.has_next()
        context['has_previous'] = page_obj.has_previous()
        context['search_query'] = search_query
        return context


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
        images = ImageForPage.objects.filter(category=ImageForPage.WORKSHOP)

        context['images'] = images
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
        images = ImageForPage.objects.filter(category=ImageForPage.SEMINAR)

        context['images'] = images
        context['seminar_list'] = page_obj
        context['num_placeholders'] = num_placeholders
        context['has_next'] = page_obj.has_next()
        context['has_previous'] = page_obj.has_previous()
        context['search_query'] = search_query
        return context


def coming_soon_view(request):
    return render(request, 'coming_soon.html')


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

        # For the timeline
        seminars_all = Seminar.objects.all().order_by('date')
        context['seminars_all'] = seminars_all

        # Next upcoming seminar
        now = timezone.now()
        next_seminar = Seminar.objects.filter(date__gte=now).order_by('date').first()
        context['next_seminar'] = next_seminar

        # Flag to check if all events have passed
        context['all_events_over'] = not next_seminar

        landing = landing_page.objects.last()

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
        if not cart.cartitem_set.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart_detail')

        total = sum(item.total_price() for item in cart.cartitem_set.all())
        payment_method = PaymentMethod.objects.last()
        form = PaymentProofForm()
        return render(request, 'tickets/checkout.html', {
            'cart': cart,
            'total': total,
            'form': form,
            'payment_method': payment_method
        })

    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        total_str = request.POST.get('final_total', None)

        if total_str is not None:
            try:
                total = float(total_str)
            except ValueError:
                total = sum(item.total_price() for item in cart.cartitem_set.all())
        else:
            total = sum(item.total_price() for item in cart.cartitem_set.all())

        order = Order.objects.create(user=request.user)

        # Create OrderItems from CartItems and update ticket categories
        for cart_item in cart.cartitem_set.all():
            OrderItem.objects.create(
                order=order,
                ticket_category=cart_item.ticket_category,
                quantity=cart_item.quantity,
                price=cart_item.ticket_category.price,  # Store the price at time of purchase
            )
            # Update ticket category
            ticket_category = cart_item.ticket_category
            ticket_category.booked_seats += cart_item.quantity
            ticket_category.reserved_seats -= cart_item.quantity
            ticket_category.save()

        # Now we can safely delete the cart items
        cart.cartitem_set.all().delete()

        # Process payment proof and send email
        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            proof = form.save(commit=False)
            proof.order = order
            proof.price_paid = total
            proof.save()

            email_subject = 'Your Order Confirmation'
            email_body = render_to_string('tickets/emails/payment_received.html', {
                'user': request.user,
                'cart': cart,
                'order': order,
                'total': int(total),
            })
            email = EmailMessage(
                email_subject,
                email_body,
                'admin@jump2025.com',
                [request.user.email],
            )
            email.content_subtype = 'html'
            email.send()

            # Handle discount code usage (if applicable)
            if request.POST.get('discount_code_form') == "True":
                code = request.POST.get('discount_code_name')
                discount_code = get_object_or_404(DiscountCode, code=code)
                if discount_code.is_valid():
                    discount_code.used_count += 1
                    discount_code.save()

        return redirect('order_confirmed')


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
                new_total = round(new_total)  # Round to the nearest integer

                # Format the total for display
                formatted_total = "Rp " + f"{int(new_total):,}".replace(",", ".")

                return JsonResponse({
                    'success': True,
                    'new_total_formatted': formatted_total,
                    'new_total_numeric': str(new_total)
                })
            else:
                return JsonResponse({'success': False, 'message': 'Invalid or expired discount code.'})
        except DiscountCode.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid discount code.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})


@staff_member_required
def admin_dashboard(request):
    orders = Order.objects.all().order_by('-created_at')
    seminars = Seminar.objects.all().order_by('date')

    # Aggregate order items for each order
    for order in orders:
        # Aggregate order items by seminar and ticket category
        items_dict = {}
        for order_item in order.orderitem_set.all():
            seminar = order_item.ticket_category.seminar
            ticket_category = order_item.ticket_category
            key = (seminar.id, ticket_category.id)
            if key in items_dict:
                items_dict[key]['quantity'] += order_item.quantity
            else:
                items_dict[key] = {
                    'seminar': seminar,
                    'ticket_category': ticket_category,
                    'quantity': order_item.quantity,
                }
        # Convert the aggregated items to a list
        order.aggregated_items = list(items_dict.values())

    return render(request, 'tickets/admin_dashboard.html', {'orders': orders, 'seminars': seminars})


@staff_member_required
def scicom_dashboard(request):
    scicom = SciComSubmission.objects.all()
    context = {
        'scicom': scicom
    }
    return render(request, 'tickets/scicom_dashboard.html', context)


@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'orders': orders})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    for order in orders:
        # Aggregate order items by seminar and ticket category
        items_dict = {}
        for order_item in order.orderitem_set.all():
            seminar = order_item.ticket_category.seminar
            ticket_category = order_item.ticket_category
            key = (seminar.id, ticket_category.id)
            if key in items_dict:
                items_dict[key]['quantity'] += order_item.quantity
            else:
                items_dict[key] = {
                    'seminar': seminar,
                    'ticket_category': ticket_category,
                    'quantity': order_item.quantity,
                }
        # Convert the aggregated items to a list
        order.aggregated_items = list(items_dict.values())

    return render(request, 'tickets/order_history.html', {'orders': orders})


class SeminarDetailView(DetailView):
    model = Seminar
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'seminar'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seminar = self.get_object()
        context['ticket_categories'] = seminar.ticket_categories.all()

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
    item_count = cart.cartitem_set.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    return JsonResponse({'item_count': item_count})


class CartDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        is_empty = not cart.cartitem_set.exists()
        cart_items = cart.cartitem_set.all()
        return render(request, 'tickets/cart_detail.html',
                      {'cart': cart, 'is_empty': is_empty, 'cart_items': cart_items})


class RemoveFromCartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart_item = get_object_or_404(CartItem, id=kwargs['item_id'])
        cart_item.delete()
        return redirect('cart_detail')


class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'not_authenticated'})

        ticket_category_id = request.POST.get('ticket_category_id')
        ticket_category = get_object_or_404(TicketCategory, id=ticket_category_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            ticket_category=ticket_category,
            defaults={'quantity': 0}
        )

        quantity = int(request.POST.get('quantity', 1))

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        if ticket_category.remaining_seats < quantity:
            return JsonResponse({'success': False, 'message': 'Not enough remaining seats'})

        cart_item.save()

        response = {
            'success': True,
            'message': 'Added to cart successfully!',
            'quantity': cart_item.quantity,
            'remaining_seats': ticket_category.remaining_seats,
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

    email_subject = 'Konfirmasi Pesanan Anda'
    email_body = render_to_string('tickets/emails/order_confirmed.html', {
        'user': order.user,
    })
    email = EmailMessage(
        email_subject,
        email_body,
        'admin@jump2025.com',
        [order.user.email],
    )
    email.content_subtype = 'html'

    try:
        email.send()
    except Exception as e:
        messages.error(request, f"Failed to send email: {e}")
    return redirect('admin_dashboard')


@staff_member_required
def export_orders_view(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"

    # 1) Add "Email" to your headers:
    headers = [
        'Username', 'Email', 'Nama Lengkap', 'NIK', 'NPWP', 'Institution',
        'No. Telfon', 'Order ID', 'Created At', 'Confirmed',
        'Confirmation Date', 'Seminars', 'Total Price'
    ]
    ws.append(headers)

    # 2) Iterate over *all* orders:
    all_orders = Order.objects.all()

    for order in all_orders:
        created_at_naive = order.created_at.replace(tzinfo=None) if order.created_at else None
        confirmation_date_naive = (
            order.confirmation_date.replace(tzinfo=None)
            if order.confirmation_date
            else None
        )

        # -- Aggregate seminars & tickets, same as before --
        items_dict = {}
        for order_item in order.orderitem_set.all():
            seminar = order_item.ticket_category.seminar
            ticket_category = order_item.ticket_category
            key = (seminar.id, ticket_category.id)
            if key in items_dict:
                items_dict[key]['quantity'] += order_item.quantity
            else:
                items_dict[key] = {
                    'seminar_title': seminar.title,
                    'seminar_date': seminar.date.strftime('%Y-%m-%d'),
                    'ticket_category_name': ticket_category.name,
                    'quantity': order_item.quantity,
                }

        # Create a single string describing all seminars & categories
        seminars_list = []
        for item in items_dict.values():
            seminars_list.append(
                f"{item['seminar_title']} ({item['seminar_date']}) - "
                f"{item['ticket_category_name']} - "
                f"Quantity: {item['quantity']}"
            )
        seminars_str = "; ".join(seminars_list)

        payment_proof = PaymentProof.objects.filter(order=order).first()
        price_paid = float(payment_proof.price_paid) if payment_proof else 0.0

        user = order.user
        full_name = user.nama_lengkap
        phone_number = user.Nomor_telpon
        nik = user.nik
        institution = user.institution
        email = user.email  # <--- retrieve from user model


        # 3) Append data including "Email" to the row:
        ws.append([
            user.username,
            email,
            full_name,
            nik,
            user.npwp,
            institution,
            phone_number,
            order.id,
            created_at_naive,
            'Yes' if order.is_confirmed else 'No',
            confirmation_date_naive,
            seminars_str,
            price_paid,
        ])

    # Optional number formatting for the price (the 12th column now)
    for row in ws.iter_rows(min_row=2, min_col=12, max_col=12):  # 12 = 'L' column if starting at 'A' = 1
        for cell in row:
            cell.number_format = '#,##0'

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="order_report.xlsx"'
    wb.save(response)

    return response


@staff_member_required
def export_orders_for_seminar_view(request, seminar_id):
    from django.shortcuts import get_object_or_404
    seminar = get_object_or_404(Seminar, pk=seminar_id)

    # 1) Filter all Orders that have any OrderItem referencing this seminar
    orders_for_seminar = (
        Order.objects
        .filter(orderitem__ticket_category__seminar=seminar)
        .distinct()
    )

    wb = Workbook()
    ws = wb.active
    sanitized_title = re.sub(r'[\/:*?"<>|]', '', f"Orders for {seminar.title}")
    ws.title = sanitized_title

    # 2) Same headers (including "Email"):
    headers = [
        'Username', 'Email', 'Nama Lengkap', 'NIK', 'NPWP', 'Institution',
        'No. Telfon', 'Order ID', 'Created At', 'Confirmed',
        'Confirmation Date', 'Seminars', 'Total Price'
    ]
    ws.append(headers)

    for order in orders_for_seminar:
        created_at_naive = (
            order.created_at.replace(tzinfo=None) if order.created_at else None
        )
        confirmation_date_naive = (
            order.confirmation_date.replace(tzinfo=None)
            if order.confirmation_date
            else None
        )

        # --- same item aggregation logic as before ---
        items_dict = {}
        for order_item in order.orderitem_set.all():
            seminar_item = order_item.ticket_category.seminar
            ticket_category = order_item.ticket_category
            key = (seminar_item.id, ticket_category.id)
            if key in items_dict:
                items_dict[key]['quantity'] += order_item.quantity
            else:
                items_dict[key] = {
                    'seminar_title': seminar_item.title,
                    'seminar_date': seminar_item.date.strftime('%Y-%m-%d'),
                    'ticket_category_name': ticket_category.name,
                    'quantity': order_item.quantity,
                }

        seminars_list = []
        for item in items_dict.values():
            seminars_list.append(
                f"{item['seminar_title']} ({item['seminar_date']}) "
                f"- {item['ticket_category_name']} "
                f"- Quantity: {item['quantity']}"
            )
        seminars_str = "; ".join(seminars_list)

        payment_proof = PaymentProof.objects.filter(order=order).first()
        price_paid = float(payment_proof.price_paid) if payment_proof else 0.0

        user = order.user

        ws.append([
            user.username,
            user.email,
            user.nama_lengkap,
            user.nik,
            user.npwp,
            user.institution,
            user.Nomor_telpon,
            order.id,
            created_at_naive,
            'Yes' if order.is_confirmed else 'No',
            confirmation_date_naive,
            seminars_str,
            price_paid,
        ])

    # Optional: format the total price column
    for row in ws.iter_rows(min_row=2, min_col=12, max_col=12):
        for cell in row:
            cell.number_format = '#,##0'

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"orders_for_{seminar.title.replace(' ', '_')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)

    return response


def export_scicom_submissions_excel(request):
    # Create a new workbook
    workbook = Workbook()

    # We will create three querysets:
    abstracts = SciComSubmission.objects.filter(submission_type=SciComSubmission.ABSTRACT).select_related('user')
    videos   = SciComSubmission.objects.filter(submission_type=SciComSubmission.VIDEO).select_related('user')
    flyers   = SciComSubmission.objects.filter(submission_type=SciComSubmission.FLYER).select_related('user')

    # ---------------------------------------------------
    # 1) ABSTRACT Submissions (first sheet)
    # ---------------------------------------------------
    abstract_ws = workbook.active  # The first sheet is active by default
    abstract_ws.title = "Abstract Submissions"

    # Columns we want for abstracts
    abstract_columns = [
        "ID",
        "Name",
        "Occupation",
        "Email",
        "Phone",
        "Affiliation",
        "Address",
        "Already Registered?",
        "Created At",
        "Abstract Title",
        "Paper Type",
        "Abstract Authors",
        "Abstract Text",
        "Link Abstract",
    ]

    # Write the header row
    row_num = 1
    for col_num, column_title in enumerate(abstract_columns, start=1):
        cell = abstract_ws.cell(row=row_num, column=col_num, value=column_title)

    # Populate data rows for abstracts
    for submission in abstracts:
        row_num += 1
        # Convert booleans or other fields to readable strings
        registered_str = "Yes" if submission.already_registered else "No"
        occupation_str = submission.get_occupation_display()

        abstract_ws.cell(row=row_num, column=1,  value=submission.id)
        abstract_ws.cell(row=row_num, column=2,  value=submission.name)
        abstract_ws.cell(row=row_num, column=3,  value=occupation_str)
        abstract_ws.cell(row=row_num, column=4,  value=submission.email)
        abstract_ws.cell(row=row_num, column=5,  value=submission.phone)
        abstract_ws.cell(row=row_num, column=6,  value=submission.affiliation)
        abstract_ws.cell(row=row_num, column=7,  value=submission.address)
        abstract_ws.cell(row=row_num, column=8,  value=registered_str)
        # format created_at
        created_str = submission.created_at.strftime("%Y-%m-%d %H:%M:%S")
        abstract_ws.cell(row=row_num, column=9,  value=created_str)

        abstract_ws.cell(row=row_num, column=10, value=submission.abstract_title)
        abstract_ws.cell(row=row_num, column=11, value=submission.paper_type)
        abstract_ws.cell(row=row_num, column=12, value=submission.abstract_authors)
        abstract_ws.cell(row=row_num, column=13, value=submission.abstract_text)
        abstract_ws.cell(row=row_num, column=14, value=submission.link_abstract)

    # ---------------------------------------------------
    # 2) VIDEO Submissions (second sheet)
    # ---------------------------------------------------
    video_ws = workbook.create_sheet("Video Submissions")

    # Columns for video
    video_columns = [
        "ID",
        "Name",
        "Occupation",
        "Email",
        "Phone",
        "Affiliation",
        "Address",
        "Already Registered?",
        "Created At",
        "Video Title",
        "Video Authors",
        "Link Video",
    ]

    # Header
    row_num = 1
    for col_num, column_title in enumerate(video_columns, start=1):
        cell = video_ws.cell(row=row_num, column=col_num, value=column_title)

    # Populate data for videos
    for submission in videos:
        row_num += 1
        registered_str = "Yes" if submission.already_registered else "No"
        occupation_str = submission.get_occupation_display()
        created_str = submission.created_at.strftime("%Y-%m-%d %H:%M:%S")

        video_ws.cell(row=row_num, column=1,  value=submission.id)
        video_ws.cell(row=row_num, column=2,  value=submission.name)
        video_ws.cell(row=row_num, column=3,  value=occupation_str)
        video_ws.cell(row=row_num, column=4,  value=submission.email)
        video_ws.cell(row=row_num, column=5,  value=submission.phone)
        video_ws.cell(row=row_num, column=6,  value=submission.affiliation)
        video_ws.cell(row=row_num, column=7,  value=submission.address)
        video_ws.cell(row=row_num, column=8,  value=registered_str)
        video_ws.cell(row=row_num, column=9,  value=created_str)

        video_ws.cell(row=row_num, column=10, value=submission.video_title)
        video_ws.cell(row=row_num, column=11, value=submission.video_authors)
        video_ws.cell(row=row_num, column=12, value=submission.link_video)

    # ---------------------------------------------------
    # 3) FLYER Submissions (third sheet)
    # ---------------------------------------------------
    flyer_ws = workbook.create_sheet("Flyer Submissions")

    flyer_columns = [
        "ID",
        "Name",
        "Occupation",
        "Email",
        "Phone",
        "Affiliation",
        "Address",
        "Already Registered?",
        "Created At",
        "Flyer Title",
        "Flyer Authors",
        "Link Flyer",
    ]

    row_num = 1
    for col_num, column_title in enumerate(flyer_columns, start=1):
        cell = flyer_ws.cell(row=row_num, column=col_num, value=column_title)

    for submission in flyers:
        row_num += 1
        registered_str = "Yes" if submission.already_registered else "No"
        occupation_str = submission.get_occupation_display()
        created_str = submission.created_at.strftime("%Y-%m-%d %H:%M:%S")

        flyer_ws.cell(row=row_num, column=1,  value=submission.id)
        flyer_ws.cell(row=row_num, column=2,  value=submission.name)
        flyer_ws.cell(row=row_num, column=3,  value=occupation_str)
        flyer_ws.cell(row=row_num, column=4,  value=submission.email)
        flyer_ws.cell(row=row_num, column=5,  value=submission.phone)
        flyer_ws.cell(row=row_num, column=6,  value=submission.affiliation)
        flyer_ws.cell(row=row_num, column=7,  value=submission.address)
        flyer_ws.cell(row=row_num, column=8,  value=registered_str)
        flyer_ws.cell(row=row_num, column=9,  value=created_str)

        flyer_ws.cell(row=row_num, column=10, value=submission.flyer_title)
        flyer_ws.cell(row=row_num, column=11, value=submission.flyer_authors)
        flyer_ws.cell(row=row_num, column=12, value=submission.link_flyer)

    # ---------------------------------------------------
    # Generate Response
    # ---------------------------------------------------
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = "scicom_submissions_multi_" + datetime.datetime.now().strftime("%Y%m%d") + ".xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    workbook.save(response)
    return response