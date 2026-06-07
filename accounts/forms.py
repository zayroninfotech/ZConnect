from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email address'}))
    display_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Display name (optional)'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'display_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('display_name', 'email', 'bio', 'phone', 'avatar', 'status')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell something about yourself...'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone number'}),
            'display_name': forms.TextInput(attrs={'placeholder': 'Display name'}),
        }
