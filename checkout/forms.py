from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:

        # Meta options inform django what model
        # this class will be associated with
        model = Order

        # Notice we're not rendering any fields in the forms
        # which need to be calculated, that's due to the fact
        # that nobody will ever be filling that information out
        # Those will be done via the model methods we've created
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)

    # Overidding the init method of the form allows us
    # to customize it
    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        # First we call the default init method to set the form
        #  up as it would be by default
        super().__init__(*args, **kwargs)

        # Dict of placeholders, which will be placeholders for
        # their respective fields
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
        }

        # We're then autofocusing on the full_name field
        self.fields['full_name'].widget.attrs['autofocus'] = True

        # We then iterate over the fields
        for field in self.fields:
            if field != "country":
                # Add * for each required field
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                
                # Give them their respective placeholders & classes
                self.fields[field].widget.attrs['placeholder'] = placeholder

            # Follow stripe css in the checkout css file
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'

            # We're also removing the labels as placeholders are now set
            self.fields[field].label = False
