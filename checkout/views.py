from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from profiles.forms import UserProfileForm
from profiles.models import UserProfile
from bag.contexts import bag_contents

import stripe
import json

@require_POST
def cache_checkout_data(request):
    """
    Before the confirm card payment in stripe_elements.js is called,
    a post request is made to this view, providing it the client secret
    from the payment intent.
    """
    try:
        # Split at the word secret to get the payment intent id
        pid = request.POST.get('client_secret').split("_secret")[0]

        # Setup stripe with the secret id so we can modify payment intent
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Modify payment intent with it's id and modify it with metadata
        stripe.PaymentIntent.modify(pid, metadata={
            "username": request.user,
            "save_info": request.POST.get("save_info"),
            "bag": json.dumps(request.session.get("bag"))
        })

        # Return a http response with a status of ok
        return HttpResponse(status=200)
    except Exception as e:

        messages.error(request, "Sorry, your payment cannot be processed right now. Please try again later")
        return HttpResponse(content=e, status=400)

def checkout(request):
    """
    Render the checkout template
    """

    # Beginning of creation of stripe payment intent
    # get keys from env variables
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == "POST":
        # Get bag from session
        bag = request.session.get("bag", {})

        form_data = {
            "full_name": request.POST["full_name"],
            "email": request.POST["email"],
            "phone_number": request.POST["phone_number"],
            "country": request.POST["country"],
            "postcode": request.POST["postcode"],
            "town_or_city": request.POST["town_or_city"],
            "street_address1": request.POST["street_address1"],
            "street_address2": request.POST["street_address2"],
            "county": request.POST["county"],
        }

        # Create an order form instance using the form_data dict
        order_form = OrderForm(form_data)

        # If the form is valid
        if order_form.is_valid():
            # We'll save the order, giving it a variable so we can use it
            # within the redirect function at the bottom
            # Commit = False adds optimization, preventing the first save
            # from happening
            order = order_form.save(commit=False)

            # Obtain client secret by getting from form and splitting
            pid = request.POST.get('client_secret').split("_secret")[0]

            # Apply client secret to stripe pid in order
            order.stripe_pid = pid

            # Place bag within original bag paramter of order
            # Json.dumps converts Python object to json string
            order.original_bag = json.dumps(bag)

            # Save the order
            order.save()

            # We'll then iterate through the bag items to create line items
            for item_id, item_data in bag.items():
                try:
                    # Get the product id from the bag
                    product = Product.objects.get(id=item_id)

                    # If it's data (value) is an int,
                    #  we know we're dealing with an
                    # item that has no sizes, therefore
                    # the item data is the quantity as reflected in dict below
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    # otherwise if it not an integer
                    # We'll iterate over each size and create
                    # a line item accordingly
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                # Despite this being unlikely,
                # We'll error handle if a product does not exist by
                # Sending a message, delete order & redirect user to bag page
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))

            # Whilst still in loop, we'll attach whether the user wanted to
            # save their profile information to the session
            request.session['save_info'] = 'save-info' in request.POST

            # Redirect user to checkout success page, passing the order no.
            # as an argument
            return redirect(reverse('checkout_success', args=[order.order_number]))

        else:
            # If the order form is not valid, let's send a message letting
            # them know and send them back to the checkout page
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')

    else:

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

        # If the user is authenticated
        if request.user.is_authenticated:
            # Get their profile & make it the initial
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    "full_name": profile.user.get_full_name(),
                    "email": profile.user.email,
                    "phone_number": profile.default_phone_number,
                    "country": profile.default_country,
                    "postcode": profile.default_postcode,
                    "town_or_city": profile.default_town_or_city,
                    "street_address1": profile.default_street_address1,
                    "street_address2": profile.default_street_address2,
                    "county": profile.default_county
                })
            # If not, we'll render an empty form
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
       
        else:
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


def checkout_success(request, order_number):
    """
    Take the order number & render a checkout success page
    To inform the order is now complete.
    """
    # Check user wanted their info saved by checking the session
    save_info = request.session.get('save_info')

    # Get the order using the order_number created in the view
    # above, which we'll send back to the template
    order = get_object_or_404(Order, order_number=order_number)

    # If the user has an authenticated profile
    if request.user.is_authenticated:
        # Get user's profile
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.user_profile = profile
        # Save it
        order.save()

        # If save info checkbox was checked, Save user's info
        if save_info:
            # By pulling the data to go in the user's profile
            # matches the fields within user profile model
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }

            # Create instance of user profile form, using profile_data
            # Telling it we're updating the profile we've obtained above
            user_profile_form = UserProfileForm(profile_data, instance=profile)

            # If form is valid, save it
            if user_profile_form.is_valid():
                user_profile_form.save()

    # Attach a success message, letting the user know what their
    # order number is and that an email will be sent to the one
    # typed in within the order form
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    # Delete the bag from the session, since it'll no
    # longer be needed for this session
    if 'bag' in request.session:
        del request.session['bag']

    # Get the template
    template = 'checkout/checkout_success.html'

    # Set the context
    context = {
        'order': order,
    }

    return render(request, template, context)
