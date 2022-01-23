from django.shortcuts import render, redirect

# Create your views here.


def view_bag(request):
    """
    View that renders the bag contents page
    """
    return render(request, "bag/bag.html")


def add_to_bag(request, item_id):
    """
    Add a quantity pf the specified product to the shopping bag
    """

    # Get's returned as a string by default, we'll convert
    # it to an integer and store the quantity
    quantity = int(request.POST.get("quantity"))

    # Grabs the specified url from the post request
    # Telling us where to re-direct to after this view is completed
    redirect_url = request.POST.get("redirect_url")

    # Grab the session bag if it exists
    # Initialise a new dictionary if it doesn't
    bag = request.session.get("bag", {})

    # If there's already a key in the bag, that matches
    # the current product id, increment it accordingly
    # else give it the amount specified within from request
    if item_id in list(bag.keys()):
        bag[item_id] += quantity
    else:
        bag[item_id] = quantity
    
    # Place the bag dictionary within the session
    request.session['bag'] = bag
    print(request.session["bag"])
    return redirect(redirect_url)
