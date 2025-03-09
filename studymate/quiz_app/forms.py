from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User, UserProfile
from django import forms

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    name = forms.CharField(required=True)  
    class Meta:
        model = UserProfile
        fields = ["avatar", "institution", "field_of_study", "bio"]

    def save(self, commit=True):
        profile = super().save(commit=False)

        if self.cleaned_data.get("avatar"):
            profile.avatar = self.cleaned_data["avatar"]

        if commit:
            profile.save()
        return profile

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = None  # We don’t need the old password field
    new_password1 = forms.CharField(required=False)
    new_password2 = forms.CharField(required=False)