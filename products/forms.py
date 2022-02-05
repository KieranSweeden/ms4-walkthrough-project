from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """Forms for products"""
    class Meta:
        """Defines the model and fields included"""
        model = Product
        # Get all the fields from Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """Override init method to make changes to fields"""
        super().__init__(*args, **kwargs)

        # We want the categories to show up in the form
        # Using friendly names
        # Get all categories
        categories = Category.objects.all()

        # Create a list of tuples of the friendly names
        # Associated with their category id's
        # Using list comprehension
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        # Withfriendly names, update the category field on the form
        # Using those for choices instead of using the id
        self.fields['category'].choices = friendly_names

        # Then iterate through the rest of the fields
        # Setings classes to make them match the theme
        # of the rest of our store
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
