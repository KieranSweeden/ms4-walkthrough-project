from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import StripeWH_Handler

import stripe

# require.POST means it only accepts post requests
# stripe doesn't send csrf token so it needs to be exempt
@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe"""
    # Setup stripe api key and webhook secret
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    print(stripe.api_key)

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    # Create instance of the stripe web hook handler function
    handler = StripeWH_Handler(request)

    # Map webhook events to relevant handler functions
    # keys will match the names of webhooks coming from stripe
    # while it's values will be actual methods inside the webhook handler
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    # Get the webhook event type from Stripe
    # Will return something along the lines of "payment_intent.succeeded" or
    # "payment_intent.payment_failed"
    event_type = event['type']

    # Look up key in event_map dictionary above and assign it's value
    # to a variable called event_handler
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the event handler with the event
    # event_handler is nothing more than an alias for whatever function is pulled
    # from the event_map dictionary, that means we can call it
    # here we're getting the reponse from the event_handler and passing it the event
    response = event_handler(event)

    # Return the response to stripe
    return response