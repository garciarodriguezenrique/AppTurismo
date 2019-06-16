from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

class SignupForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label=mark_safe("<strong>Nombre de usuario</strong>"))
    email = forms.EmailField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}), label=mark_safe("<strong>Correo electrónico</strong>"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label=mark_safe("<strong>Introduce una contaseña</strong>"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label=mark_safe("<strong>Repite tu contraseña</strong>"))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class AccModForm(UserCreationForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label=mark_safe("<strong>Introduce la contraseña actual</strong>"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label=mark_safe("<strong>Introduce la nueva contaseña</strong>"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label=mark_safe("<strong>Repite la nueva contraseña</strong>"))

    class Meta:
        model = User
        fields = ('old_password','password1', 'password2')
        

class ImageUploadForm(forms.Form):
    caption = forms.CharField(max_length=250)
    image = forms.ImageField()
