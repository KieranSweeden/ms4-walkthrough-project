from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from checkout.models import Order

from .models import UserProfile
from .forms import UserProfileForm



def profile(request):
    """ Display the user's profile. """

    # get profile for the current user
    profile = get_object_or_404(UserProfile, user=request.user)

    # If the request is post
    if request.method == "POST":

        # Create a new instance of the user
        # profile form using the post data
        # telling it the instance we're updating is
        # the profile variable above
        form = UserProfileForm(request.POST, instance=profile)

        # If form is valid, save & send success message
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")

    # Build instance of form using the profile
    form = UserProfileForm(instance=profile)

    # Get profile's order history
    orders = profile.orders.all()

    template = 'profiles/profile.html'

    # Issue occurs where updating a user profile,
    # Success message also shows bag, which is un-related & awkward
    # on_profile_page set to true allows us to control this
    context = {
        "form": form,
        "orders": orders,
        "on_profile_page": True
    }

    return render(request, template, context)


def order_history(request, order_number):
    """
    Displays order history
    """

    # Grab order from order model above
    order = get_object_or_404(Order, order_number=order_number)

    # Add message informing user they're looking
    # at past order information
    messages.info(request, (
        f'This is a past confirmation for order number {order_number}.'
        'A confirmation emal was sent on the order date.'
    ))

    # Re-use the checkout_success template as it already
    # has the layout for rendering order confirmation
    template = 'checkout/checkout_success.html'

    # Add from_profile variable so we can check from
    # the checkout_success template if we arrived from
    # the order_history view
    context = {
        'order': order,
        'from_profile': True
    }

    return render(request, template, context)
