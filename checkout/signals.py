from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order
from services.models import Booking


@receiver(post_save, sender=Booking)
def update_order_total_on_save(sender, instance, **kwargs):
    if instance.order:
        instance.order.update_totals()


@receiver(post_delete, sender=Booking)
def update_order_total_on_delete(sender, instance, **kwargs):
    if instance.order:
        instance.order.update_totals()
