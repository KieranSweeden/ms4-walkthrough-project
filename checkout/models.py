import uuid

from django.db import models
from django.db.models import Sum
from django.conf import settings

from django_countries.fields import CountryField

from products.models import Product
from profiles.models import UserProfile

# Flow of these models
# 1. first use the information given within a payment form to create an instance of Order
# 2. We'll then iterate through the items in the shopping bag
# 3. During this iteration, we'll be creating a new instance of OrderLineItem for each item,
# attaching it to the order and updating the delivery costs, order total and grand total
# (being Order fields) along the way

class Order(models.Model):

    # editable = false is self explanatory - this will be a unique & permanent no.
    # so it cannot be edited
    order_number = models.CharField(max_length=32, null=False, editable=False)

    # create new foreign key to user profile model
    # We're using models.SET_NULL if profile is deleted since it will allow
    # us to keep an order history in the admin even is user is deleted
    # null & blank being true allows anonymous users to make purchases
    # related_name set to orders in this case allows us to access the
    # user's orders by calling something like user.userProfile.orders (in this case)
    user_profile = models.ForeignKey(UserProfile,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True,
                                     related_name='orders')

    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)

    # Doesn't have placeholder as it's a select box
    # However we do have the blank_label property to act as a placeholder
    country = CountryField(blank_label="Country", null=False, blank=False)

    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)

    # auto_now_add attribute automatically set this field (in this case, the date & time)
    date = models.DateTimeField(auto_now_add=True)

    # These 3 will be updated by the OrderLineItems when attached
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)

    # These two fields are to combat the likelihood in which the same customer
    # could make the same order twice on different occasions, which would result
    # in us finding the first order, thus the second order is not added

    # Contains the original shopping bad that created it
    original_bag = models.TextField(null=False, blank=False, default="")

    # Contains the stripe payment intent ID which is guarunteed to be unique
    stripe_pid = models.CharField(max_length=254, null=False, blank=False, default="")

    # prepended with _ to indicate it's a private method that'll
    # only be used inside this class
    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        # By using the sum function across all the lineitem total fields
        # for all line items within this order
        # Default behaviour is to add a new field to the query set called "lineitem_total__sum"
        # Which we can get and set the order total to that
        # or 0 is added as an error handling measure, as the following line under the this code expects an int
        # without or 0, it returns none, which would cause an error as the if statment below would
        # attempt to see if delivery threshold is less than none, which isn't good
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0

        # With order total calculated, we can then calculate the delivery cost
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            # If the order total is under the threshold, the delivery cost is the total multiplied
            # by standard delivery percentage
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            # If the order total is over the threshold, the delivery cost is 0
            self.delivery_cost = 0

        # Determine grand total by adding delivery cost & order total together
        self.grand_total = self.order_total + self.delivery_cost

        # Save the order instance
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


# Line-item = individual shopping bag item, relating to a specific order and referencing
# the product itself, the size selected, quantity and total cost for that line item
class OrderLineItem(models.Model):
    # Using a related_name for foreign key field allows us to make calls such as:
    # order.lineitems.all or order.lineitems.filter (it's lineitems in this case, as we chose that name)
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')

    # There's also a foreign key for products, so we can access all fields of the associated
    # product as well
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)

    product_size = models.CharField(max_length=2, null=True, blank=True) # XS, S, M, L, XL
    quantity = models.IntegerField(null=False, blank=False, default=0)

    # Is un-editable as it'll automatically be calculated when the line item is saved
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)


    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'