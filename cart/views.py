from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from services.models import Service

@login_required
def add_to_cart(request, service_id):
    """ Add a service booking to the cart """
    if request.method == 'POST':
        try:
            service_id = str(service_id)  
        except ValueError:
            messages.error(request, 'Invalid service ID.')
            return redirect('services:services')

        service = get_object_or_404(Service, id=service_id)
        date = request.POST.get('date')
        time = request.POST.get('time')
        cart = request.session.get('cart', {})

        if service_id in cart:
            messages.info(request, 'Service already in cart.')
        else:
            cart[service_id] = {
                'service_id': service_id,
                'name': service.name,
                'price': str(service.price),
                'description': service.description,
                'date': date,
                'time': time,
            }
            messages.success(request, f'{service.name} added to cart.')

        additional_service_id = request.POST.get('additional_service')
        if additional_service_id:
            try:
                additional_service_id = str(additional_service_id)  
                additional_service = get_object_or_404(Service, id=additional_service_id)
                additional_booking_date = request.POST.get('additional_booking_date')
                additional_booking_time = request.POST.get('additional_booking_time')

                if additional_service_id in cart:
                    messages.info(request, 'Additional service already in cart.')
                else:
                    cart[additional_service_id] = {
                        'service_id': additional_service_id,
                        'name': additional_service.name,
                        'price': str(additional_service.price),
                        'description': additional_service.description,
                        'date': additional_booking_date,
                        'time': additional_booking_time,
                    }
                    messages.success(request, f'{additional_service.name} added to cart.')
            except ValueError:
                messages.error(request, 'Invalid additional service ID.')

        request.session['cart'] = cart
        return redirect('cart:view_cart')

    return redirect('services:services')


@login_required
def remove_from_cart(request, service_id):
    """ Remove a service booking from the cart """
    service_id = str(service_id)  
    cart = request.session.get('cart', {})

    if service_id in cart:
        del cart[service_id]
        request.session['cart'] = cart
        messages.success(request, 'Service removed from cart.')
    else:
        messages.error(request, 'Service not found in cart.')

    return redirect('cart:view_cart')


def view_cart(request):
    cart = request.session.get('cart', {})
    booking_items = []
    total = Decimal('0.00')

    for service_id, item in cart.items():
        service = get_object_or_404(Service, id=service_id)
        price = Decimal(item['price'])
        total += price
        booking_items.append({
            'service': service,
            'price': price,
            'name': item['name'],
            'description': item['description'],
            'date': item['date'],
            'time': item['time'],
        })

    additional_booking_id = request.session.get('additional_booking_id')
    if additional_booking_id:
        additional_booking_service = get_object_or_404(Service, id=additional_booking_id)
        additional_booking = {
            'service': additional_booking_service,
            'date': request.session.get('additional_booking_date'),
            'time': request.session.get('additional_booking_time'),
        }
    else:
        additional_booking = None

    context = {
        'cart': booking_items,
        'total': total,
        'additional_booking': additional_booking,
    }
    return render(request, 'cart/cart.html', context)

@login_required
def checkout(request):
    """ View to handle checkout process """
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:view_cart')
    
    booking_items = []
    total = Decimal('0.00')

    for service_id, item in cart.items():
        service = get_object_or_404(Service, id=service_id)
        price = Decimal(item['price'])
        total += price
        booking_items.append({
            'service': service,
            'price': price,
            'name': item['name'],
            'description': item['description'],
            'date': item['date'],
            'time': item['time'],
        })

    context = {
        'cart': booking_items,
        'total': total,
    }

    if request.method == 'POST':
      
        messages.success(request, 'Checkout completed successfully.')
        request.session['cart'] = {}  
        return redirect('services:services')

    return render(request, 'cart/checkout.html', context)