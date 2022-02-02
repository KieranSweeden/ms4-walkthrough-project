from django.contrib import admin
# Importing order and orderlineitem models
from .models import Order, OrderLineItem

# Inherits from tabularinline
class OrderLineItemAdminInline(admin.TabularInline):
    # This inline item will allow us to add & edit line items within admin
    # With the order model
    model = OrderLineItem

    # Make line item total read-only
    readonly_fields = ('lineitem_total',)


class OrderAdmin(admin.ModelAdmin):
    # Add line item as an inline item for orderadmin class
    inlines = (OrderLineItemAdminInline,)

    # Fields that are not editable and are calculated by our model methods
    readonly_fields = ('order_number', 'date',
                       'delivery_cost', 'order_total',
                       'grand_total', "original_bag", "stripe_pid")

    # Add fields option which isn't entirely necessary
    # However, it allows us to tell django how we want the fields to be ordered in admin
    # Without this, django would adjust it accordingly due to the use of some read-only fields
    # Now the order will stay the same as the way it is within the model
    fields = ('order_number', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost',
              'order_total', 'grand_total', "original_bag", "stripe_pid")

    # Restrict the columns that show up in the order to only a few key items
    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total',)

    # The items will be ordered by date in reverse, placing most recent orders at the top
    ordering = ('-date',)

# Register Order & OrderAdmin model
# We're not going to register the OrderLineItem model, since
# It's accessible via the inline within the order model
admin.site.register(Order, OrderAdmin)