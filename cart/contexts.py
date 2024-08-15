from decimal import Decimal
from django.shortcuts import get_object_or_404
from services.models import Service
from packages.models import Package


def cart_contents(request):
    """Retrieves the contents of the cart from the session, calculates the total price,
    and provides the details of the items in the cart. """
    # Retrieve the cart from the session, defaulting to an empty dictionary if not found
    cart = request.session.get('cart', {})
    booking_items = []  # List to hold details of items in the cart
    total = Decimal('0.00')  # Initialize total cost of items
    service_count = 0  # Initialize count of items
    # Iterate through each item in the cart
    for item_key, item in cart.items():
        try:
            # Split item_key into type (service/package) and ID
            item_type, item_id = item_key.split('_')
            # Process service items
            if item_type == 'service':
                # Retrieve the service object or return 404 if not found
                service = get_object_or_404(Service, id=int(item_id))
                # Append service details to booking_items
                booking_items.append({
                    'service': service,
                    'price': Decimal(item['price']),
                    'name': item['name'],
                    'description': item['description'],
                })
                # Add price to total and increment the service count
                total += Decimal(item['price'])
                service_count += 1
            # Process package items
            elif item_type == 'package':
                # Retrieve the package object or return 404 if not found
                package = get_object_or_404(Package, id=int(item_id))
                # Append package details to booking_items
                booking_items.append({
                    'package': package,
                    'price': Decimal(item['price']),
                    'name': item['name'],
                    'description': item['description'],
                })
                # Add price to total and increment the service count
                total += Decimal(item['price'])
                service_count += 1
        # Handle exceptions if item does not exist or ID is invalid
        except (Service.DoesNotExist, Package.DoesNotExist, ValueError):
            pass
    # Check if there's an additional service ID stored in the session
    additional_service_id = request.session.get('additional_service_id')
    if additional_service_id:
        try:
            # Retrieve the additional service object or return 404 if not found
            additional_service = get_object_or_404(Service, id=additional_service_id)
            # Append additional service details to booking_items
            additional_item = {
                'service': additional_service,
                'price': additional_service.price,
                'name': additional_service.name,
                'description': additional_service.description,
            }
            booking_items.append(additional_item)
            # Add price to total and increment the service count
            total += additional_service.price
            service_count += 1
        # Handle exception if additional service does not exist
        except Service.DoesNotExist:
            pass
    # Set grand_total to the calculated total
    grand_total = total
    # Prepare context to be returned
    context = {
        'booking_items': booking_items,
        'total': total,
        'service_count': service_count,
        'grand_total': grand_total,
    }

    return context
