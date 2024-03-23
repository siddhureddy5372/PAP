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

    def validate_password(self, password):
        # Overriding this method to bypass default password validation
        return password
    
class ProfileForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Profile
        fields = ["Profile_image", 'first_name', 'last_name', 'gender', 'dob']

        widgets = {
            'Profile_image': forms.FileInput(attrs={'class': 'form-control',"required":False}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': False}),  
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': False}),  
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': False}), 
        }