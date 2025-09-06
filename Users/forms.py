# In your Users/forms.py file
from django import forms
from .models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        # Include all possible fields here
        fields = [
            'profile_picture', 'business_name', 'first_name', 'last_name', 
            'email', 'username', 'bio'
        ]
        # Define widgets for consistent styling
        widgets = {
            'business_name': forms.TextInput(),
            'username': forms.TextInput(),
            'first_name': forms.TextInput(),
            'last_name': forms.TextInput(),
            'email': forms.EmailInput(),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'profile_picture': forms.FileInput(attrs={'id': 'id_profile_picture'}),
        }

    def __init__(self, *args, **kwargs):
        """
        This method customizes the form fields based on the user's role.
        """
        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        user = self.instance

        # Apply Tailwind classes to all fields dynamically
        field_classes = 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all text-base bg-slate-50'
        for field_name, field in self.fields.items():
            if field_name != 'profile_picture':
                 field.widget.attrs.update({'class': field_classes})

        # If the user is a turf owner, remove player-specific fields
        if user and user.is_turf_owner:
            del self.fields['username']
            del self.fields['bio']
        # If the user is a player, remove owner-specific fields
        else:
            del self.fields['business_name']