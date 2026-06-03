from django import forms
from .models import Livre, AvisLivre, ImageLivre


class LivreForm(forms.ModelForm):
    class Meta:
        model = Livre
        fields = [
            "titre", "auteur", "categorie", "description", "prix", "prix_promo",
            "type_vente", "fichier_pdf", "prix_pdf",
            "langue", "isbn", "nombre_pages", "maison_edition", "date_publication",
            "quantite_stock", "disponible", "en_vedette", "image_principale"
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "date_publication": forms.DateInput(attrs={"type": "date"}),
            "prix_pdf": forms.NumberInput(attrs={"placeholder": "Laisser vide = même prix"}),
        }
        help_texts = {
            "fichier_pdf": "Fichier PDF du livre (uniquement pour vente numérique)",
            "prix_pdf": "Laisser vide pour utiliser le même prix que la version physique",
        }


class AvisForm(forms.ModelForm):
    class Meta:
        model = AvisLivre
        fields = ["note", "commentaire"]
        widgets = {
            "commentaire": forms.Textarea(attrs={"rows": 4, "placeholder": "Partagez votre avis sur ce livre..."}),
        }


class RechercheForm(forms.Form):
    q = forms.CharField(required=False, label="Rechercher", widget=forms.TextInput(attrs={"placeholder": "Titre, auteur, ISBN..."}))
    categorie = forms.CharField(required=False)
    langue = forms.CharField(required=False)
    prix_min = forms.DecimalField(required=False, min_value=0)
    prix_max = forms.DecimalField(required=False, min_value=0)
