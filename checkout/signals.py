from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import OrderLineItem

# Functions within this file are called each time a line item
# is attached to an order

# IMPORTANT
# post_.... in this case means after, not sending something
# so post_save would mean, after saving perform this function
# These signals are sent by django to the entire application after
# A model instance is saved and after it's deleted respectively

# @reciever is how we recieve these signals
# So in the examples below, we're setting up these functions to recieve
# signals on if a OrderLineItem has been saved or deleted respectively.

@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    # instance.order is the order this line item is related to
    # call the update_total method on it
    instance.order.update_total()

@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.order.update_total()