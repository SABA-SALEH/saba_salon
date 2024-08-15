from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _


class CustomClearableFileInput(ClearableFileInput):
    """
    A custom file input widget that extends Django's ClearableFileInput.
    """
    # Label for the checkbox that appears if the user wants to remove the current file
    clear_checkbox_label = _('Remove')
    # Text displayed next to the current file preview
    initial_text = _('Current Image')
    # Text displayed next to the file input field
    input_text = _('')
    # Path to the custom template used to render this widget
    template_name = 'team/custom_widget_templates/custom_clearable_file_input.html'
