from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Nombre de usuario")
    email = forms.EmailField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Introduce una contaseña")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Repite tu contraseña")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class AccModForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Introduce la nueva contaseña")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Repite la nueva contraseña")

    class Meta:
        model = User
        fields = ('password1', 'password2')
        

class ImageUploadForm(forms.Form):
    caption = forms.CharField(max_length=250)
    image = forms.ImageField()
