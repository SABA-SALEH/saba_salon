from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _


class CustomClearableFileInput(ClearableFileInput):
    # Label for the checkbox that allows users to clear the current file
    clear_checkbox_label = _('Remove')
    # Text to be displayed when there is an initial file
    initial_text = _('Current Image')
    # Text to be displayed for the file input field itself
    input_text = _('')
    # Path to the custom template used for rendering this widget
    template_name = 'services/custom_widget_templates/custom_clearable_file_input.html'
