from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from bag.contexts import bag_contents

import stripe


def checkout(request):
    """
    Render the checkout template
    """

    # Beginning of creation of stripe payment intent
    # get keys from env variables
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Get bag from session
    bag = request.session.get("bag", {})

    # If there's nothing in the bag, provide an
    # error message and redirect user to product page
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse("products"))
    
    # Since it returns a dict, send the function the request
    # And get the same dictionary here in the view
    current_bag = bag_contents(request)

    # To get total, we just need to get the grand_total from current bag
    total = current_bag['grand_total']

    # Multiply total by 100 and round it to zero decimal places
    # as stipe requires the amount to charge as an integer
    stripe_total = round(total * 100)

    # Set the secret key to stripe
    stripe.api_key = stripe_secret_key

    # Create payment intent, giving it the amount & currency
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
        payment_method_types=["card"],
    )

    # Now we're creating an instance of our order
    # that'll be empty for now
    order_form = OrderForm()

    # Convenient messages that alerts you if public key is not set
    if not stripe_public_key:
        messages.warning(request, "Stripe public key is missing, did you forget to set it?")

    # Then create the template
    template = "checkout/checkout.html"

    # Create the context containing the newly
    # initialised form
    context = {
        "order_form": order_form,
        "stripe_public_key": stripe_public_key,
        "client_secret": intent.client_secret,
    }

    # Render the template with it's context
    return render(request, template, context)
