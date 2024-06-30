from decimal import Decimal
from services.models import Service

def cart_contents(request):
    cart = request.session.get('cart', {})
    booking_items = []
    total = Decimal('0.00')
    service_count = 0

    for service_id, item in cart.items():
        service = Service.objects.get(id=service_id)
        booking_items.append({
            'service': service,
            'price': Decimal(item['price']),
            'name': item['name'],
            'description': item['description'],
        })
        total += Decimal(item['price'])
        service_count += 1

    additional_service_id = request.session.get('additional_service_id')
    if additional_service_id:
        additional_service = Service.objects.get(id=additional_service_id)
        additional_item = {
            'service': additional_service,
            'price': additional_service.price,
            'name': additional_service.name,
            'description': additional_service.description,
        }
        booking_items.append(additional_item)
        total += additional_service.price
        service_count += 1

    grand_total = total

    context = {
        'booking_items': booking_items,
        'total': total,
        'service_count': service_count,
        'grand_total': grand_total,
    }

    return context
