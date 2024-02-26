from django import forms
from .models import ClosetClothes

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ClosetClothes
        fields = ['image', 'brand', 'model', 'color', 'category', 'subcategory', 'waterproof']
        widgets = {
            'brand': forms.TextInput(attrs={'style': 'text-transform: capitalize;'}),
            'model': forms.TextInput(attrs={'style': 'text-transform: capitalize;'}),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ImageUploadForm, self).__init__(*args, **kwargs)

    def clean_model(self):
        model = self.cleaned_data.get('model')
        # If model is empty, set it to None
        if not model:
            return "Unknown"
        return model

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance


class AIDetectionForm(forms.ModelForm):
    class Meta:
        model = ClosetClothes
        fields = ['image', 'brand', 'model', 'waterproof']
        widgets = {
            'brand': forms.TextInput(attrs={'style': 'text-transform: capitalize;'}),
            'model': forms.TextInput(attrs={'style': 'text-transform: capitalize;'}),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AIDetectionForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance