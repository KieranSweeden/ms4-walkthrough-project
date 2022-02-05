# Srtipe sends out webhook messages for events like payment intent created
# Webhooks are similar to django signals, except that they're sent securely
# from stripe to a URL we specify, hence including httpresponse below
from django.http import HttpResponse

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile

import json
import time


class StripeWH_Handler:
    """Handles Stripe webhooks"""

    def __init__(self, request):
        # The init method of the class is a setup method that's called
        # everytime an instance of this class is created.
        # Here, we're assigning the request as an attribute of the class
        # in case we need to access any attributes of the request coming from stripe
        self.request = request


    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        Takes the event stripe is sending to us and simply
        return a http response indicating it was recieved
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)


    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        # Our metadata should be attached in the key of object
        # within data within the passed in event
        intent = event.data.object

        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        billing_details = intent.charges.data[0].billing_details

        shipping_details = intent.shipping

        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # To ensure the data is in the same form as what we want in our database
        # We'll replace any empty strings in the shipping details with None, as
        # Stripe stores empty field values as empty strings which is not the same
        # As the null value we want in the database
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked
        # Start with profile set to none, allowing anonymous users to checkout
        profile = None

        # Get username from intent
        username = intent.metadata.username
        
        # If the username is anything but AnonymousUser
        # We know they're an authenticated user
        if username != "AnonymousUser":
            # Get profile from authenticated user
            profile = UserProfile.objects.get(user__username=username)

            # If save info box checked
            if save_info:
                # Update profile by adding the shipping details 
                # as their default delivery information
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state

                # Save profile
                profile.save()

        # Let's start by assuming that this order doesn't currently already exist
        order_exists = False

        # Instead of immediately going to create the order if it's not in the database
        # let's introduce a delay
        attempt = 1

        # Allow for up to 5 attempts at finding the order
        while attempt <= 5:

            try:
                order = Order.objects.get(
                    # __iexact looks for an exact match and is case insensitive
                    full_name__iexact=shipping_details.name,
                    user_profile=profile,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid
                )
                order_exists = True

                # Break out of the while loop if the order is found
                break

            except Order.DoesNotExist:

                # This was a failed attempt to increment the attempt variable
                attempt += 1

                # This will in effect, cause the webhook handler to try to find the order
                # five times over 5 seconds before giving up and creating the order itself
                time.sleep(1)

        if order_exists:
            return HttpResponse(
                    content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                    status=200)

        else:

            # Order could not be found, therefore it's set to none
            order = None 

            try:
                # We don't have a form to save in the web hook to create the order
                # But we can do it with ordered objects created using all the data
                # From the payment intent, after all it did come from the form originally
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid
                )

                # Here we're loading the bag from the JSON version within payment intent
                for item_id, item_data in json.loads(bag).items():

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
        
            except Exception as e:
                # If anything goes wrong, we'll just delete the order
                # If it was created and return a 500 server error response to stripe
                # This will cause stripe to try the web hook again later
                if order:
                    order.delete()
                    return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=500)

        return HttpResponse(content=f'Webhook received: {event["type"]} | SUCCESS: Created Order in webhook',
                            status=200)


    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
