from django import forms
from django.core.exceptions import ValidationError
from .models import StaffMember
from .widgets import CustomClearableFileInput
import re

class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = ['name', 'position', 'bio', 'photo', 'email', 'phone_number']
        widgets = {
            'photo': CustomClearableFileInput,
        }

    def clean_name(self):
        """
        Validate that the name contains only letters and spaces and is unique,
        except for the current instance when editing.
        """
        name = self.cleaned_data.get('name')

        if not name:
            raise ValidationError("Name cannot be empty.")
        
        # Only allow letters and spaces
        if not re.match(r'^[A-Za-z\s]+$', name):
            raise ValidationError("Name must contain only letters and spaces.")
        
        if len(name) < 3:
            raise ValidationError("Name must be at least 3 characters long.")
        
        # Check for uniqueness, excluding the current instance
        if StaffMember.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A team member with this name already exists.")
        
        return name

    def clean_position(self):
        """
        Validate that the position contains only letters and spaces.
        """
        position = self.cleaned_data.get('position')
        if not position:
            raise ValidationError("Position cannot be empty.")
        
        if not re.match(r'^[A-Za-z\s]+$', position):  # Only allow letters and spaces
            raise ValidationError("Position must contain only letters and spaces.")
        
        if len(position) < 3:
            raise ValidationError("Position must be at least 3 characters long.")
        
        return position

    def clean_bio(self):
        """
        Validate that the bio is not empty and is at least 10 characters long.
        """
        bio = self.cleaned_data.get('bio')
        if not bio:
            raise ValidationError("Bio cannot be empty.")
        
        if len(bio) < 10:
            raise ValidationError("Bio must be at least 10 characters long.")
        
        return bio

    def clean_email(self):
        """
        Validate that the email address is valid.
        """
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email cannot be empty.")
        
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):  # Basic email format validation
            raise ValidationError("Enter a valid email address.")
        
        return email

    def clean_phone_number(self):
        """
        Validate that the phone number contains only digits and is of a reasonable length.
        """
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise ValidationError("Phone number cannot be empty.")
        
        if not phone_number.isdigit():
            raise ValidationError("Phone number must contain only digits.")
        
        if len(phone_number) < 8 or len(phone_number) > 15:  # Basic length check
            raise ValidationError("Phone number must be between 10 and 15 digits.")
        
        return phone_number

    def clean(self):
        """
        Perform form-wide validation if needed.
        """
        cleaned_data = super().clean()
        return cleaned_data
