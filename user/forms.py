from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return password2

    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['Profile_image','first_name', 'last_name', 'gender', 'dob']

    def clean(self):
        cleaned_data = super().clean()
        required_fields = ['first_name', 'last_name', 'gender', 'dob']
        for field in required_fields:
            if not cleaned_data.get(field):
                raise forms.ValidationError(f"{field} is required.")
        return cleaned_data