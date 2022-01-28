from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm

def checkout(request):
    """
    Render the checkout template
    """
    # Get bag from session
    bag = request.session.get("bag", {})

    # If there's nothing in the bag, provide an
    # error message and redirect user to product page
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse("products"))
    
    # Now we're creating an instance of our order
    # that'l be empty for now
    order_form = OrderForm()

    # Then create the template
    template = "checkout/checkout.html"

    # Create the context containing the newly
    # initialised form
    context = {
        "order_form": order_form
    }

    # Render the template with it's context
    return render(request, template, context)