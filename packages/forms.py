import re
from django import forms
from .models import Package
from services.models import Service


class PackageForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Package
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black'

    def clean_name(self):
        """
        Ensure the name is not empty, contains only letters and spaces, 
        is at least 3 characters long, and is unique, except for the current instance when editing.
        """
        name = self.cleaned_data.get('name')

        if not name:
            raise forms.ValidationError('Name cannot be empty.')

        if not re.match(r'^[A-Za-z\s]+$', name):
            raise forms.ValidationError('Name must contain only letters and spaces.')

        if len(name) < 3:
            raise forms.ValidationError('Name must be at least 3 characters long.')

        if Package.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A package with this name already exists.')

        return name

    def clean_description(self):
        """
        Ensure the description is not empty and is sufficiently long.
        """
        description = self.cleaned_data.get('description')

        if not description:
            raise forms.ValidationError('Description cannot be empty.')

        if len(description) < 10:
            raise forms.ValidationError('Description must be at least 10 characters long.')

        return description

    def clean_price(self):
        """
        Ensure the price is not empty and greater than 0.
        """
        price = self.cleaned_data.get('price')

        if price is None:
            raise forms.ValidationError('Price cannot be empty.')

        if price <= 0:
            raise forms.ValidationError('Price must be greater than zero.')

        return price

    def clean_saving_price(self):
        """
        Ensure the saving price is not negative and less than the price.
        """
        price = self.cleaned_data.get('price')
        saving_price = self.cleaned_data.get('saving_price')

        if saving_price is None:
            raise forms.ValidationError('Saving price cannot be empty.')

        if saving_price < 0:
            raise forms.ValidationError('Saving price cannot be negative.')

        if price is None:
            raise forms.ValidationError('Price must be provided before checking saving price.')

        if saving_price >= price:
            raise forms.ValidationError('Saving price must be less than the price.')

        return saving_price

    def clean_services(self):
        """
        Ensure at least one service is selected.
        """
        services = self.cleaned_data.get('services')

        if not services:
            raise forms.ValidationError('You must select at least one service.')

        return services

    def clean(self):
        """
        Form-wide validation.
        """
        cleaned_data = super().clean()
        return cleaned_data
