from django import forms
from django.core.exceptions import ValidationError
from .models import Order
import re

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            placeholder = placeholders.get(field, '')
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False

    def clean_full_name(self):
        """
        Validate that the full name contains only letters and spaces.
        """
        full_name = self.cleaned_data.get('full_name')
        if not full_name:
            raise ValidationError("Full name cannot be empty.")
        
        if not re.match(r'^[A-Za-z\s]+$', full_name):  # Only allow letters and spaces
            raise ValidationError("Full name must contain only letters and spaces.")
        
        if len(full_name) < 3:
            raise ValidationError("Full name must be at least 3 characters long.")
        
        return full_name

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
