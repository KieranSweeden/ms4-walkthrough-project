from django.shortcuts import render, get_object_or_404
from .models import Product

# Create your views here.
def all_products(request):
    """
    View to show all producuts, including sorting & search queries
    """

    # Return all products within database using all()
    products = Product.objects.all()

    # Add products to context to send them to template
    context = {
        "products": products
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