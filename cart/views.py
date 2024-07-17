from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from datetime import datetime
from services.models import Service, Booking
from packages.models import Package
from datetime import datetime
from django.http import JsonResponse

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

        item_key = f'service_{service_id}'
        
        if item_key in cart:
            messages.info(request, 'Service already in cart.')
        else:
            cart[item_key] = {
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

                item_key_additional = f'service_{additional_service_id}'

                if item_key_additional in cart:
                    messages.info(request, 'Additional service already in cart.')
                else:
                    cart[item_key_additional] = {
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
        request.session.modified = True
        return redirect('cart:view_cart')

    return redirect('services:all_services')


def remove_from_cart(request, item_type, item_id):
    """ Remove a service or package booking from the cart """
    item_key = f'{item_type}_{item_id}'  
    cart = request.session.get('cart', {})

    if item_key in cart:
        del cart[item_key]
        request.session['cart'] = cart
        messages.success(request, f'{item_type.capitalize()} removed from cart.')
    else:
        messages.error(request, f'{item_type.capitalize()} not found in cart.')

    request.session.modified = True
    return redirect('cart:view_cart')


def view_cart(request):
    cart = request.session.get('cart', {})
    services = []
    packages = []
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
            services.append({
                'service': service,
                'price': price,
                'name': item['name'],
                'description': item['description'],
                'date': item.get('date'), 
                'time': item.get('time'), 
            })
        elif item_type == 'package':
            package = get_object_or_404(Package, id=item_id)
            price = Decimal(item['price'])
            total += price
            packages.append({
                'package': package,
                'price': price,
                'name': item['name'],
                'description': item['description'],
            })

    context = {
        'cart': {
            'services': services,
            'packages': packages,
        },
        'total': total,
    }
    return render(request, 'cart/cart.html', context)


def edit_cart_item(request, service_id):
    cart = request.session.get('cart', {})
    item_key = f'service_{service_id}'
    print("Cart data at the start:", cart)  

    if item_key not in cart:
        messages.error(request, 'Service not found in cart.')
        return redirect('cart:view_cart')

    service = get_object_or_404(Service, id=int(service_id))
    item = cart[item_key]
    print("Editing item:", item)  

    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        print("Received date:", date)  
        print("Received time:", time) 

        if not date or not time:
            messages.error(request, 'Date or time cannot be empty.')
            return redirect('cart:view_cart')

        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            time = datetime.strptime(time, '%H:%M').time()
        except ValueError:
            messages.error(request, 'Invalid date or time format.')
            return redirect('cart:view_cart')

        existing_bookings = Booking.objects.filter(service=service, date=date).values_list('time', flat=True)
        if existing_bookings.exists() and not (date.isoformat() == item['date'] and time.strftime('%H:%M') == item['time']):
            messages.error(request, f'The time slot {time.strftime("%H:%M")} on {date.strftime("%Y-%m-%d")} is already booked. Please choose another time.')
            return redirect('cart:view_cart')

        item['date'] = date.isoformat()
        item['time'] = time.strftime('%H:%M')

        cart[item_key] = item
        request.session['cart'] = cart
        request.session.modified = True
        print("Updated cart data:", cart)  
        messages.success(request, f'{service.name} updated in cart.')
        return redirect('cart:view_cart')

    available_times = service.get_available_times(datetime.now().date())

    context = {
        'service': service,
        'item': item,
        'available_times': available_times,
    }

    return render(request, 'cart/cart.html', context) 


def get_booked_times(request, service_id):
    if request.method == 'GET' and 'booking_date' in request.GET:
        service = get_object_or_404(Service, pk=service_id)
        booking_date = request.GET['booking_date']
        booked_times_qs = Booking.objects.filter(service=service, date=booking_date).values_list('time', flat=True)
        booked_times = list(booked_times_qs)
        data = {
            'booked_times': booked_times
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def get_available_times(request, service_id):
    if request.method == 'GET' and 'booking_date' in request.GET:
        service = get_object_or_404(Service, pk=service_id)
        booking_date = request.GET['booking_date']
        available_times = service.get_available_times(booking_date)
        data = {
            'available_times': available_times
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def add_package_to_cart(request, item_id):
    try:
        item_id = int(item_id) 
    except ValueError:
        messages.error(request, 'Invalid package ID.')
        return redirect('packages:package_list')

    cart = request.session.get('cart', {})

    item_key = f'package_{item_id}'

    if item_key in cart:
        messages.info(request, 'Package already in cart.')
    else:
        package = get_object_or_404(Package, id=item_id)
        cart[item_key] = {
            'package_id': item_id,
            'name': package.name,
            'price': str(package.price),
            'description': package.description,
        }


        messages.success(request, f'{package.name} added to cart.')

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart:view_cart')