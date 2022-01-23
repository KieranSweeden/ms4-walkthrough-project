from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

# This is a context processor
# It's purpose is to make this dictionary available to
# All templates across the entire application
# This is made widely available by adding it to the list of context processors within
# The app's settings.py file
def bag_contents(request):

    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get("bag", {})

    for item_id, quantity in bag.items():
        product = get_object_or_404(Product, pk=item_id)
        total += quantity * product.price
        product_count += quantity
        bag_items.append({
            "item_id": item_id,
            "quantity": quantity,
            "product": product,
        })

    if total < settings.FREE_DELIVERY_THRESHOLD:
        # Decimal function is used since we're dealing with financial transactions
        # and using floats is susceptible to rounding errors
        # Generally, using decimal is preffered when working with money as it's more accruate
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)

        # Calculate the amount needed to qualify for free delivery, enticing
        # The customer to purchase more
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    
    else:

        delivery = 0
        free_delivery_delta = 0
    
    grand_total = delivery + total

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total
    }   

    return context