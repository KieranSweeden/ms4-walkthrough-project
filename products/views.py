from django.shortcuts import render
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