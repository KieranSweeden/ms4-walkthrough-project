from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product

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

    # Get the product
    product = get_object_or_404(Product, pk=item_id)

    # Get's returned as a string by default, we'll convert
    # it to an integer and store the quantity
    quantity = int(request.POST.get("quantity"))

    # Grabs the specified url from the post request
    # Telling us where to re-direct to after this view is completed
    redirect_url = request.POST.get("redirect_url")

    # Init's the size to none as some products are only one size
    size = None

    # If a product size is present within request,
    # Replace the initial value with the requested one
    if 'product_size' in request.POST:
        size = request.POST['product_size']


    # Grab the session bag if it exists
    # Initialise a new dictionary if it doesn't
    bag = request.session.get("bag", {})

    if size:
        if item_id in list(bag.keys()):
            # If the item is already in the bag, check to see if another item of the same id
            # and same size already exists. If so, increment the quantity for that size
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['items_by_size'][size] += quantity
                # Otherwise, set the amount of this item in a particular size to the quantity,
                # As this is a new size for that item
                messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
            else:
                bag[item_id]['items_by_size'][size] = quantity
                # Message user that a new size has been added
                messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
        else:
            # If item is not already present within bag, add it to the bag
            # We're doing it as a dictionary with the key of items_by_size, as we
            # May have multiple items with this item_id, but different sizes.
            # This allows us to structure the bags such that we can have a single item_id for each item,
            #  But still track multiple sizes
            bag[item_id] = {'items_by_size': {size: quantity}}
            # Message user that a new size has been added
            messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
    else:

        # If there's already a key in the bag, that matches
        # the current product id, increment it accordingly
        # else give it the amount specified within from request
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
            # Send message informing the quantity has been updated
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            bag[item_id] = quantity

            # Add a message to request object, informing the user that the item
            # Has been added to their bag
            messages.success(request, f'Added {product.name} to your bag')
  
    # Place the bag dictionary within the session
    request.session['bag'] = bag

    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """
    Adjust the quantity of of the specified product to the specified amount
    """

    # Get the product
    product = get_object_or_404(Product, pk=item_id)

    # Get's returned as a string by default, we'll convert
    # it to an integer and store the quantity
    quantity = int(request.POST.get("quantity"))

    # Init's the size to none as some products are only one size
    size = None

    # If a product size is present within request,
    # Replace the initial value with the requested one
    if 'product_size' in request.POST:
        size = request.POST['product_size']


    # Grab the session bag if it exists
    # Initialise a new dictionary if it doesn't
    bag = request.session.get("bag", {})

    if size:
        if quantity > 0:
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
        else:
            del bag[item_id]['items_by_size'][size]

            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')

    else:
        if quantity > 0:
            bag[item_id] = quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            bag.pop(item_id)
            # Inform user that item has been removed from bag
            messages.success(request, f'Removed {product.name} from your bag')
  
    # Place the bag dictionary within the session
    request.session['bag'] = bag

    return redirect(reverse('view_bag'))

def remove_from_bag(request, item_id):
    """
    Remove the item from the shopping bag
    """

    try:
        # Get product
        product = get_object_or_404(Product, pk=item_id)

        # Init's the size to none as some products are only one size
        size = None

        # If a product size is present within request,
        # Replace the initial value with the requested one
        if 'product_size' in request.POST:
            size = request.POST['product_size']


        # Grab the session bag if it exists
        # Initialise a new dictionary if it doesn't
        bag = request.session.get("bag", {})

        if size:
            del bag[item_id]['items_by_size'][size]

            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')

        else:
            bag.pop(item_id)
            # Inform user that item has been removed from bag
            messages.success(request, f'Removed {product.name} from your bag')
    
        # Place the bag dictionary within the session
        request.session['bag'] = bag

        # Instead of a redirect, because this view will be posted to from a javascript function,
        # We want to return an actuall 200 HTTP response, implying that the item was
        # Successfully removed
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f"Error removing item: {e}")
        return HttpResponse(status=500)

