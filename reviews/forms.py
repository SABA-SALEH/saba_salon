from django import forms
from .models import Review
from services.models import Service
from packages.models import Package

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def __init__(self, *args, **kwargs):
        entity = kwargs.pop('initial', {}).get('service') or kwargs.pop('initial', {}).get('package')
        super().__init__(*args, **kwargs)
        
        if isinstance(entity, Service):
            self.fields['service'] = forms.ModelChoiceField(queryset=Service.objects.all(), initial=entity, widget=forms.HiddenInput())
            self.fields.pop('package', None)
        elif isinstance(entity, Package):
            self.fields['package'] = forms.ModelChoiceField(queryset=Package.objects.all(), initial=entity, widget=forms.HiddenInput())
            self.fields.pop('service', None)