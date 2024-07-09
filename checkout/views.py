from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .forms import OrderForm
from services.models import Service , Booking
from packages.models import Package
from .models import Order

@login_required
def checkout(request):
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

            messages.success(request, 'Checkout completed successfully.')
            request.session['cart'] = {}
            return redirect('services:all_services')
        else:
            messages.error(request, 'There was an error with your form. Please double-check your information.')

    order_form = OrderForm()

    context = {
        'cart': booking_items,
        'total': total,
        'order_form': order_form,
    }

    return render(request, 'checkout/checkout.html', context)
