from django import forms
from .models import StaffMember
from .widgets import CustomClearableFileInput

class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = ['name', 'position', 'bio', 'photo', 'email', 'phone_number']
        widgets = {
            'photo': CustomClearableFileInput,
        }
