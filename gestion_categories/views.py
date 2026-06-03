from django.shortcuts import render, get_object_or_404
from .models import Categorie
from gestion_livres.models import Livre


def liste_categories(request):
    categories = Categorie.objects.filter(active=True, parent__isnull=True).prefetch_related(
        "sous_categories", "livres"
    )
    return render(request, "gestion_categories/liste.html", {"categories": categories})


def livres_par_categorie(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug, active=True)

    livres = Livre.objects.filter(disponible=True)
    if categorie.sous_categories.exists():
        sous_ids = list(categorie.sous_categories.values_list("id", flat=True))
        sous_ids.append(categorie.id)
        livres = livres.filter(categorie__id__in=sous_ids)
    else:
        livres = livres.filter(categorie=categorie)

    tri = request.GET.get("tri", "-created_at")
    livres = livres.order_by(tri)

    return render(request, "gestion_categories/livres.html", {
        "categorie": categorie,
        "livres": livres,
        "total": livres.count(),
    })
