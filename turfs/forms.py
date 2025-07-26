# turfs/forms.py

from django import forms
from .models import Turf

class TurfForm(forms.ModelForm):
    """
    Form for Turf Owners to add or edit turf details.
    Uses Django's ModelForm to automatically create fields based on the Turf model.
    """
    class Meta:
        model = Turf
        # Fields that the turf owner can directly edit
        fields = ['name', 'location', 'description', 'price_per_hour', 'image', 'is_active']
        # Customize labels for better user experience
        labels = {
            'name': 'Turf Name',
            'location': 'Location (e.g., City, Area)',
            'description': 'Description (Optional)',
            'price_per_hour': 'Price per Hour (e.g., 1000.00 INR)',
            'image': 'Turf Image',
            'is_active': 'Make Turf Active (Visible to Players)?',
        }
        # Add widgets for better control over form field rendering
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}), # Make textarea larger
            'price_per_hour': forms.NumberInput(attrs={'min': 0, 'step': 0.01}), # Ensure positive number, allow decimals
        }

    def __init__(self, *args, **kwargs):
        """
        Custom initialization to apply Bootstrap-like classes to form fields.
        Also, makes the 'owner' field hidden as it will be set automatically by the view.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Apply a common CSS class for styling
            if field_name != 'is_active': # Checkbox doesn't need 'form-control'
                field.widget.attrs['class'] = 'form-control'
            if field_name == 'image':
                field.widget.attrs['class'] = 'form-control-file' # Specific class for file inputs

        # The 'owner' field is set by the view, so it should not be visible or editable by the user
        # It's not included in 'fields' above, but if it were, you'd hide it here:
        # self.fields['owner'].widget = forms.HiddenInput()
        # self.fields['owner'].required = False # Not required in form as it's set by view
