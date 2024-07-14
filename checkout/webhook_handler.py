from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Order
from services.models import Booking
from packages.models import Package
import json
import time
import stripe

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event['data']['object']
        pid = intent['id']
        cart = intent['metadata'].get('cart', json.dumps({}))
        save_info = intent['metadata'].get('save_info', 'false').lower() == 'true'

        billing_details = intent['charges']['data'][0]['billing_details']
        grand_total = round(intent['charges']['data'][0]['amount'] / 100, 2)


        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=billing_details['name'],
                    email__iexact=billing_details['email'],
                    phone_number__iexact=billing_details['phone'],
                    grand_total=grand_total,
                    original_bag=cart,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if not order_exists:
            order = None
            try:
                order = Order.objects.create(
                    full_name=billing_details['name'],
                    email=billing_details['email'],
                    phone_number=billing_details['phone'],
                    grand_total=grand_total,
                    original_bag=cart,
                    stripe_pid=pid,
                )

                cart_items = json.loads(cart)
                for item_id, item_data in cart_items.items():
                    if item_data['type'] == 'service':
                        service_id = item_data['service_id']
                        service = get_object_or_404(Service, id=service_id)
                        booking = Booking.objects.create(
                            user=self.request.user,
                            service=service,
                            date=item_data['date'],
                            time=item_data['time'],
                            order=order
                        )
                    elif item_data['type'] == 'package':
                        package_id = item_data['package_id']
                        package = get_object_or_404(Package, id=package_id)
                        booking = Booking.objects.create(
                            user=self.request.user,
                            package=package,
                            order=order
                        )

                order.update_totals()

            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)

        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
