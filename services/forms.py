from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Service, Category
from .widgets import CustomClearableFileInput

def generate_time_slots(start_time, end_time, duration):
    """
    Generate time slots between start_time and end_time with the specified duration.
    """
    slots = []
    current_time = start_time
    while current_time + duration <= end_time:
        slots.append(current_time.strftime('%H:%M'))
        current_time += duration
    return slots

class ServiceForm(forms.ModelForm):
    DURATION_CHOICES = [
        ('', 'Select duration'),
        ('00:15:00', '15 minutes'),
        ('00:30:00', '30 minutes'),
        ('01:00:00', '1 hour'),
        ('01:15:00', '1 hour 15 minutes'),
        ('01:30:00', '1 hour 30 minutes'),
        ('02:00:00', '2 hours'),
        ('02:30:00', '2 hours 30 minutes'),
    ]

    duration = forms.ChoiceField(
        choices=DURATION_CHOICES,
        label="Service Duration",
        required=True,
        widget=forms.Select(attrs={'class': 'border-black'})
    )

    available_times = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False,
        choices=[]
    )

    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'image': CustomClearableFileInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]
        self.fields['category'].choices = friendly_names

        # Set CSS class for each field
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black'

        self.fields['duration'].widget.attrs['placeholder'] = 'Select duration'
        self.fields['available_times'].choices = []

        # Define default start and end times
        start_time = datetime.strptime('09:00', '%H:%M')
        end_time = datetime.strptime('18:00', '%H:%M')

        # Populate choices based on the instance
        if self.instance.pk:
            # Set the initial duration value correctly
            if isinstance(self.instance.duration, timedelta):
                hours, remainder = divmod(self.instance.duration.seconds, 3600)
                minutes = remainder // 60
                duration_str = f'{hours:02}:{minutes:02}:00'
                self.fields['duration'].initial = duration_str
            
            # Generate available times based on the existing service's duration
            service_duration = self.instance.duration
            time_slots = generate_time_slots(start_time, end_time, service_duration)
            self.fields['available_times'].choices = [(time, time) for time in time_slots]

            # Preselect the stored times
            selected_times = self.instance.available_times or []
            self.initial['available_times'] = selected_times if selected_times else []

        # If the form is bound and submitted
        if self.is_bound:
            duration_str = self.data.get('duration', '')
            if duration_str:
                hours, minutes, _ = map(int, duration_str.split(':'))
                service_duration = timedelta(hours=hours, minutes=minutes)
                time_slots = generate_time_slots(start_time, end_time, service_duration)
                self.fields['available_times'].choices = [(time, time) for time in time_slots]

    def clean_name(self):
        """
        Ensure the service name contains only letters, no numbers, is at least 3 characters long, 
        and is unique, except for the current instance when editing.
        """
        name = self.cleaned_data.get('name')
        
        if not name:
            raise ValidationError("Service name cannot be empty.")
        
        # Check that the name has at least 3 characters
        if len(name) < 3:
            raise ValidationError("Name must be at least 3 characters long.")
        
        # Check for any numbers in the name
        if any(char.isdigit() for char in name):
            raise ValidationError("Service name cannot contain numbers.")
        
        # Check for uniqueness, excluding the current instance
        if Service.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A service with this name already exists.")
        
        return name



    def clean_description(self):
        description = self.cleaned_data.get('description')
        print(f"Validating description: {description}") 
        if not description:
            raise ValidationError("Description cannot be empty.")
        if len(description) < 10:  # Minimum length requirement
            raise ValidationError("Description must be at least 10 characters long.")
        return description

    def clean_price(self):
        price = self.cleaned_data.get('price')
        print(f"Validating price: {price}") 
        if price is None:
            raise ValidationError("Price cannot be empty.")
        try:
            price = float(price) 
        except (ValueError, TypeError):
            raise ValidationError("Price must be a valid number.")
        
        if price < 0:  # Check for negative price
            raise ValidationError("Price must be a positive number.")
        return price

    def clean_available_times(self):
        """
        Ensure at least one available time slot is selected.
        """
        available_times = self.cleaned_data.get('available_times')
        if not available_times:
            raise ValidationError('You must select at least one available time slot.')
        return available_times

    def clean(self):
        """
        Form-wide validation.
        """
        cleaned_data = super().clean()
        return cleaned_data
