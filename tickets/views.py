from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from .forms import PaymentProofForm, UserUpdateForm, ProfileUpdateForm
from .forms import UserRegisterForm
from .models import Seminar, Order

class baseView(ListView):
    model = Seminar
    template_name = 'index.html'

def seminar_list(request):
    seminars = Seminar.objects.all()
    return render(request, 'tickets/seminar_list.html', {'seminars': seminars})


@login_required
def create_order(request, seminar_id):
    seminar = get_object_or_404(Seminar, id=seminar_id)
    order, created = Order.objects.get_or_create(user=request.user, seminar=seminar)
    return redirect('upload_proof', order_id=order.id)


@login_required
def upload_proof(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            proof = form.save(commit=False)
            proof.order = order
            proof.save()
            return redirect('order_confirmed')
    else:
        form = PaymentProofForm()
    return render(request, 'tickets/upload_proof.html', {'form': form})


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


@login_required
def upload_proof(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            proof = form.save(commit=False)
            proof.order = order
            proof.save()
            email_subject = 'Payment Proof Received'
            email_body = render_to_string('tickets/emails/payment_received.html', {'user': request.user})
            email = EmailMessage(
                email_subject,
                email_body,
                'admin@inapro.org',
                [request.user.email],
            )
            email.content_subtype = 'html'
            email.send()
            return redirect('order_confirmed')
    else:
        form = PaymentProofForm()
    return render(request, 'tickets/upload_proof.html', {'form': form})


@staff_member_required
def admin_dashboard(request):
    orders = Order.objects.filter(is_confirmed=False)
    return render(request, 'tickets/admin_dashboard.html', {'orders': orders})


@staff_member_required
@require_POST
def confirm_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_confirmed = True
    order.confirmation_date = timezone.now()
    order.transaction_id = request.POST.get('transaction_id')
    order.save()
    email_subject = 'Order Confirmed'
    email_body = render_to_string('tickets/emails/order_confirmed.html', {'user': order.user})
    email = EmailMessage(
        email_subject,
        email_body,
        'admin@inapro.org',
        [order.user.email],
    )
    email.content_subtype = 'html'
    email.send()
    return redirect('admin_dashboard')


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'tickets/profile.html', context)


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tickets/order_history.html', {'orders': orders})
