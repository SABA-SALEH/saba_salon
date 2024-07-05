from decimal import Decimal
from django.shortcuts import get_object_or_404
from services.models import Service
from packages.models import Package  

def cart_contents(request):
    cart = request.session.get('cart', {})
    booking_items = []
    total = Decimal('0.00')
    service_count = 0

    for item_key, item in cart.items():
        try:
            item_type, item_id = item_key.split('_')
            if item_type == 'service':
                service = get_object_or_404(Service, id=int(item_id))
                booking_items.append({
                    'service': service,
                    'price': Decimal(item['price']),
                    'name': item['name'],
                    'description': item['description'],
                })
                total += Decimal(item['price'])
                service_count += 1
            elif item_type == 'package':
                package = get_object_or_404(Package, id=int(item_id))
                booking_items.append({
                    'package': package,
                    'price': Decimal(item['price']),
                    'name': item['name'],
                    'description': item['description'],
                })
                total += Decimal(item['price'])
                service_count += 1
        except (Service.DoesNotExist, Package.DoesNotExist, ValueError):
            pass

    additional_service_id = request.session.get('additional_service_id')
    if additional_service_id:
        try:
            additional_service = get_object_or_404(Service, id=additional_service_id)
            additional_item = {
                'service': additional_service,
                'price': additional_service.price,
                'name': additional_service.name,
                'description': additional_service.description,
            }
            booking_items.append(additional_item)
            total += additional_service.price
            service_count += 1
        except Service.DoesNotExist:
            pass

    grand_total = total

    context = {
        'booking_items': booking_items,
        'total': total,
        'service_count': service_count,
        'grand_total': grand_total,
    }

    return context
