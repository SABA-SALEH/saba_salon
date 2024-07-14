from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .forms import OrderForm
from services.models import Service, Booking
from packages.models import Package
from .models import Order
from django.conf import settings
from cart.contexts import cart_contents
import stripe

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
            order.order_total = total
            order.grand_total = total
            order.save()

            for item in booking_items:
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
                booking.save()

            order.update_totals()

            messages.success(request, 'Appointment booked successfully.')
            request.session['cart'] = {}
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

@login_required
def checkout_success(request, order_number, email):
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Appointment successfully booked! A confirmation email has been sent to {email}.')

    context = {
        'order': order,
        'email': email,
    }

    return render(request, 'checkout/checkout_success.html', context)
