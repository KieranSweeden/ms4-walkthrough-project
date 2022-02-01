# Srtipe sends out webhook messages for events like payment intent created
# Webhooks are similar to django signals, except that they're sent securely
# from stripe to a URL we specify, hence including httpresponse below
from django.http import HttpResponse


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

        print(intent)

        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)


    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
