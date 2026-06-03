from .models import Panier


def panier_count(request):
    if request.user.is_authenticated:
        try:
            panier = Panier.objects.get(utilisateur=request.user)
            return {"panier_count": panier.nombre_articles()}
        except Panier.DoesNotExist:
            return {"panier_count": 0}
    return {"panier_count": 0}
