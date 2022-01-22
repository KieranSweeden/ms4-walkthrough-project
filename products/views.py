from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages

# Q object used to generate search query
# Using search filtering ob objects generically, only allows
# && logic. So it'll filter down to those object that match the
# query with it's product name AND description
# The Q object allows us to do name OR description
from django.db.models import Q
from .models import Product, Category

# Create your views here.
def all_products(request):
    """
    View to show all producuts, including sorting & search queries
    """

    # Return all products within database using all()
    products = Product.objects.all()
    query = None
    categories = None

    if request.GET:

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
            
    # Add products to context to send them to template
    context = {
        "products": products,
        "search_term": query,
        "current_categories": categories,
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