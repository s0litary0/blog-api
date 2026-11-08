from unfold.forms import UserChangeForm, UserCreationForm

# from django.contrib.admin import 
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form for User admin"""
    
    class Meta(UserCreationForm.Meta):
        """Custom user creation Meta"""
        model = User
        fields = ["first_name", "last_name", "email"]


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form for User admin"""

    class Meta(UserChangeForm.Meta):
        """Custom change creation Meta"""
        model = User
        fields = [
            "first_name", 
            "last_name", 
            "email", 
            "password", 
            "is_active", 
            "is_staff", 
            "is_superuser"
        ] # type: ignore
