from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:

        # Meta options inform django what model
        # this class will be associated with
        model = UserProfile

        # instead of fields, here we have exclude
        # Render all fields EXCLUDING the user field
        # since that should never change
        exclude = ('user',)

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
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County, State or Locality',
        }

        # We're then autofocusing on the full_name field
        self.fields['default_phone_number'].widget.attrs['autofocus'] = True

        # We then iterate over the fields
        for field in self.fields:
            if field != "default_country":
                # Add * for each required field
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                
                # Give them their respective placeholders & classes
                self.fields[field].widget.attrs['placeholder'] = placeholder

            # Follow stripe css in the checkout css file
            self.fields[field].widget.attrs['class'] = 'border-black rounded-0 profile-form-input'

            # We're also removing the labels as placeholders are now set
            self.fields[field].label = False
