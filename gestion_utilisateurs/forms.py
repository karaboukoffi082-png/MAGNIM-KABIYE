from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Utilisateur


class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse e-mail")
    first_name = forms.CharField(max_length=100, required=True, label="Prénom")
    last_name = forms.CharField(max_length=100, required=True, label="Nom")
    telephone = forms.CharField(max_length=20, required=False, label="Téléphone")

    class Meta:
        model = Utilisateur
        fields = ["username", "first_name", "last_name", "email", "telephone", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ConnexionForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur ou e-mail")


class ProfilForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ["first_name", "last_name", "email", "telephone", "adresse", "ville", "pays", "photo_profil"]
        widgets = {
            "adresse": forms.Textarea(attrs={"rows": 3}),
        }
