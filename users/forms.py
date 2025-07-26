# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, UserType

class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for user registration that includes the user_type field.
    This form allows new users to select their role (Player or Turf Owner)
    during signup. Admin users should be created via the Django admin.
    """
    # Override the default username field to make it required (it usually is, but explicit is good)
    username = forms.CharField(max_length=150, required=True)

    # Add the user_type field for selection during registration
    # Exclude ADMIN from choices as admin users are created via createsuperuser
    user_type = forms.ChoiceField(
        choices=[(UserType.PLAYER, 'Player'), (UserType.TURF_OWNER, 'Turf Owner')],
        required=True,
        label="I am a"
    )

    class Meta(UserCreationForm.Meta):
        """
        Meta class to specify the model and fields for the form.
        We're using our CustomUser model and including the 'user_type' field.
        """
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('user_type', 'email',) # Add user_type and email

    def save(self, commit=True):
        """
        Override the save method to ensure the user_type is correctly set
        when a new user is created through this form.
        """
        user = super().save(commit=False)
        user.user_type = self.cleaned_data["user_type"]
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """
    Django's default AuthenticationForm is usually sufficient for login.
    We can customize it here if needed, but for now, it's a simple alias.
    """
    pass

