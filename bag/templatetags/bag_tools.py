from django import template


register = template.Library()

# To register this filter function we apply it by grabbing an
# instance of template.Library() and applying it like below using a decorator
# To read more on this, search creating custom template tags and filters in
# Django documentation
@register.filter(name='calc_subtotal')
def calc_subtotal(price, quantity):
    return price * quantity