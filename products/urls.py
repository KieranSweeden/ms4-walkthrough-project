from django.urls import path
from . import views

# What's important to note here is that we've specified
# That the product_detail url requires an integer
# If this were left as a regular variable, it would interpret
# add/ as the value for the product_id variable
# So if we used the url to navigate to the add_product page,
# We'd actually get the product_detail page with an error,
# As django looks for the first url it can match, it matches
# with product_detail and thinkg add/ is a variable.

# Using the int: helps tell django to skip

urlpatterns = [
    path('', views.all_products, name="products"),
    path('<int:product_id>/', views.product_detail, name="product_detail"),
    path('add/', views.add_product, name="add_product"),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
]
