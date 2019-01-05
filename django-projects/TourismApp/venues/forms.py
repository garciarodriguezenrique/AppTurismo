from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1= forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password2= forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ImageUploadForm(forms.Form):
    caption = forms.CharField(max_length=250)
    image = forms.ImageField()
