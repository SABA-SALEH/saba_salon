from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Order
from services.models import Service, Booking
from packages.models import Package
import json
import time
import stripe
from profiles.models import UserProfile
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email],
            fail_silently=False
        )        

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        cart = intent.metadata.cart
        save_info = intent.metadata.save_info
        username = intent.metadata.username

        logger.info(f"Received payment_intent.succeeded event: {event}")
        logger.info(f"Metadata - cart: {cart}, save_info: {save_info}, username: {username}")

        if not hasattr(intent, 'charges') or not intent.charges.data:
            logger.error(f"Missing or empty charges for PaymentIntent ID: {pid}")
            logger.debug(f"Complete event data: {json.dumps(event, indent=2)}")
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: Missing or empty charges',
                status=400
            )

        charges = intent.charges.data
        billing_details = charges[0].billing_details
        grand_total = round(charges[0].amount / 100, 2)

        profile = None
        if username != 'AnonymousUser':
            try:
                profile = UserProfile.objects.get(user__username=username)
                if save_info:
                    profile.default_phone_number = billing_details.phone
                    profile.save()
            except UserProfile.DoesNotExist:
                logger.error(f"UserProfile with username {username} does not exist")

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=billing_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=billing_details.phone,
                    grand_total=grand_total,
                    original_cart=cart,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error retrieving order: {e}")
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500
                )

        if order_exists:
            self._send_confirmation_email(order)
            logger.info('Confirmation email sent successfully.')
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200
            )
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=billing_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=billing_details.phone,
                    original_cart=cart,
                    stripe_pid=pid,
                )
                cart_items = json.loads(cart)
                for item_key, item in cart_items.items():
                    if item['type'] == 'service':
                        service_id = item['service_id']
                        service = get_object_or_404(Service, id=service_id)
                        Booking.objects.create(
                            user=profile.user if profile else None,
                            service=service,
                            date=item['date'],
                            time=item['time'],
                            order=order
                        )
                    elif item['type'] == 'package':
                        package_id = item['package_id']
                        package = get_object_or_404(Package, id=package_id)
                        Booking.objects.create(
                            user=profile.user if profile else None,
                            package=package,
                            order=order
                        )

                order.update_totals()
            except Exception as e:
                if order:
                    order.delete()
                logger.error(f"Error creating order: {e}")
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500
                )

        self._send_confirmation_email(order)
        logger.info('Confirmation email sent successfully.')
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200
        )

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200
        )
