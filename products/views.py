from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages

# For superuser security (made sure superuser functionality is)
# only accessable to super users
from django.contrib.auth.decorators import login_required

# Q object used to generate search query
# Using search filtering ob objects generically, only allows
# && logic. So it'll filter down to those object that match the
# query with it's product name AND description
# The Q object allows us to do name OR description
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category
from .forms import ProductForm


# Create your views here.
def all_products(request):
    """
    View to show all producuts, including sorting & search queries
    """

    # Return all products within database using all()
    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:

        if 'sort' in request.GET:

            sort_key = request.GET['sort']
            sort = sort_key
            if sort_key == 'name':
                sort_key = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))

            if sort_key == "category":
                sort_key = "category__name"

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sort_key = f'-{sort_key}'

            products = products.order_by(sort_key)

        if "category" in request.GET:
            categories = request.GET["category"].split(",")
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:

            query = request.GET["q"]

            # If query is blank ""
            if not query:

                # Inform user & redirect them back to the products url
                messages.error(request, "You didn't enter any search criteria")
                return redirect(reverse("products"))

            # | makes this an OR statement
            # i in front of contains make this query case insensitive
            # This is the query to be inserted into the filter object
            # THink of this as the framework the filter filters by
            queries = Q(name__icontains=query) | Q(description__icontains=query)

            # Filter all products that match the query inserted
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    # Add products to context to send them to template
    context = {
        "products": products,
        "search_term": query,
        "current_categories": categories,
        "current_sorting": current_sorting,
    }

    return render(request, "products/products.html", context)

def product_detail(request, product_id):
    """
    View details regarding an individual product
    """

    # Return all products within database using all()
    product = get_object_or_404(Product, pk=product_id)

    # Add products to context to send them to template
    context = {
        "product": product
    }

    return render(request, "products/product_detail.html", context)

@login_required
def add_product(request):
    """ Render add product template to add a product to the store """

    if not request.user.is_superuser:

        messages.error(request, "Sorry, only store owners can do that")

        return redirect(reverse("home"))

    # If we
    if request.method == 'POST':
        # If we're posting a new product
        # Get request.files also in order to make sure
        # To capture in the image of the product if one
        # Is submitted
        form = ProductForm(request.POST, request.FILES)

        # If form is valid
        if form.is_valid():
            # Get product from saving the form
            product = form.save()

            # Inform user the product has been successfully added
            messages.success(request, 'Successfully added product!')

            # Redirect to product_detail template looking at
            # The newly created product
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        # Create an empty instance of the product form
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)

@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """

    if not request.user.is_superuser:

        messages.error(request, "Sorry, only store owners can do that")

        return redirect(reverse("home"))

    # Get the product using the product id
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        # Instantiate a product form using the posted
        # form data, to update an existing instance using the product
        form = ProductForm(request.POST, request.FILES, instance=product)

        # If the form is valid
        if form.is_valid():

            # Save the updated form
            form.save()

            # Inform user that it's been saved
            messages.success(request, 'Successfully updated product!')

            # Re-direct to the product_detail page, providing the product.id
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            # Inform user updating failed
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        # Instantiate a product form using the product
        form = ProductForm(instance=product)

        # Let user know they're editing a product
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)

@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """

    if not request.user.is_superuser:

        messages.error(request, "Sorry, only store owners can do that")

        return redirect(reverse("home"))

    # Get the product using the product_id
    product = get_object_or_404(Product, pk=product_id)

    # Delete the product
    product.delete()

    # Inform user of deletiong
    messages.success(request, 'Product deleted!')

    # Redirect user to products page
    return redirect(reverse('products'))