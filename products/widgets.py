from django.forms.widgets import ClearableFileInput
# Note the use of "as _" which means we can simply use
# _ as an alias for gettext_lazy
from django.utils.translation import gettext_lazy as _


class CustomClearableFileInput(ClearableFileInput):
    """
    Overriding the clear checkbox label, the intital text,
    the input text and the template name with our own values
    """
    clear_checkbox_label = _('Remove')
    initial_text = _('Current Image')
    input_text = _('')
    template_name = 'products/custom_widget_templates/custom_clearable_file_input.html'
