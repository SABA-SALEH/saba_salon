from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
from .forms import OrderForm
from services.models import Service, Booking
from packages.models import Package
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from .models import Order
from django.conf import settings
from cart.contexts import cart_contents
import stripe
import json
from django.contrib.auth.models import AnonymousUser


@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'cart': json.dumps(request.session.get('cart', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if not stripe_secret_key:
        messages.error(request, 'Stripe secret key is missing. Please set it in your environment variables.')
        return redirect('cart:view_cart')

    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:view_cart')

    booking_items = []
    total = Decimal('0.00')

    for item_key, item in cart.items():
        item_parts = item_key.split('_')
        if len(item_parts) != 2:
            continue

        item_type, item_id = item_parts
        item_id = int(item_id)

        if item_type == 'service':
            service = get_object_or_404(Service, id=item_id)
            price = Decimal(item['price'])
            total += price
            booking_items.append({
                'type': 'service',
                'name': item['name'],
                'description': item['description'],
                'date': item['date'],
                'time': item['time'],
                'price': price,
                'service': service,
                'service_id': item_id
            })
        elif item_type == 'package':
            package = get_object_or_404(Package, id=item_id)
            price = Decimal(item['price'])
            total += price
            booking_items.append({
                'type': 'package',
                'name': item['name'],
                'description': item['description'],
                'price': price,
                'package': package,
                'package_id': item_id,
                'services': list(package.services.all())
            })

    if request.method == 'POST':
        order_form = OrderForm(request.POST)

        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_cart = json.dumps(cart)
            order.order_total = total
            order.grand_total = total

            if request.user.is_authenticated:
                try:
                    order.user_profile = UserProfile.objects.get(user=request.user)
                except UserProfile.DoesNotExist:
                    order.user_profile = None
                order.user = request.user
            else:
                order.user_profile = None
                order.user = None

            order.save()

            for item in booking_items:
                if request.user.is_authenticated:
                    if item['type'] == 'service':
                        booking = Booking(
                            user=request.user,
                            service=item['service'],
                            date=item['date'],
                            time=item['time'],
                            order=order
                        )
                    elif item['type'] == 'package':
                        booking = Booking(
                            user=request.user,
                            package=item['package'],
                            order=order
                        )
                else:
                    continue

                try:
                    booking.save()
                except ValidationError as e:
                    messages.error(request, f'Error creating booking: {e}')
                    return redirect('cart:view_cart')

            messages.success(request, 'Appointment booked successfully.')
            request.session['cart'] = {}
            request.session['save_info'] = 'save-info' in request.POST

            return redirect(reverse('checkout:checkout_success', kwargs={'order_number': order.order_number, 'email': order.email}))
        else:
            messages.error(request, 'There was an error with your form. Please double-check your information.')

    current_cart = cart_contents(request)
    total = current_cart['grand_total']
    stripe_total = round(total * 100)
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            order_form = OrderForm(initial={
                'full_name': profile.user.get_full_name(),
                'email': profile.user.email,
                'phone_number': profile.default_phone_number,
            })
        except UserProfile.DoesNotExist:
            order_form = OrderForm()
    else:
        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. Did you forget to set it in your environment?')

    context = {
        'cart': booking_items,
        'total': total,
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, 'checkout/checkout.html', context)


def checkout_success(request, order_number, email):
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

        if save_info:
            profile_data = {
                'default_phone_number': order.phone_number,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(request, f'Appointment successfully booked! A confirmation email has been sent to {email}.')

    context = {
        'order': order,
        'email': email,
    }

    return render(request, 'checkout/checkout_success.html', context)
