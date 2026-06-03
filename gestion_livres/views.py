import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from .models import Livre, AvisLivre, Favori, TelechargementPDF
from .forms import LivreForm, AvisForm, RechercheForm
from gestion_categories.models import Categorie


def boutique(request):
    livres = Livre.objects.filter(disponible=True)
    form = RechercheForm(request.GET)

    if form.is_valid():
        q = form.cleaned_data.get("q")
        categorie = form.cleaned_data.get("categorie")
        langue = form.cleaned_data.get("langue")
        prix_min = form.cleaned_data.get("prix_min")
        prix_max = form.cleaned_data.get("prix_max")

        if q:
            livres = livres.filter(
                Q(titre__icontains=q) | Q(auteur__icontains=q) |
                Q(isbn__icontains=q) | Q(maison_edition__icontains=q)
            )
        if categorie:
            livres = livres.filter(categorie__slug=categorie)
        if langue:
            livres = livres.filter(langue__code=langue)
        if prix_min:
            livres = livres.filter(prix__gte=prix_min)
        if prix_max:
            livres = livres.filter(prix__lte=prix_max)

    tri = request.GET.get("tri", "-created_at")
    if tri in ["prix", "-prix", "-created_at", "titre"]:
        livres = livres.order_by(tri)

    paginator = Paginator(livres, 12)
    page = request.GET.get("page", 1)
    livres_page = paginator.get_page(page)

    categories = Categorie.objects.filter(active=True)
    return render(request, "gestion_livres/boutique.html", {
        "livres": livres_page,
        "categories": categories,
        "form": form,
        "total_resultats": livres.count(),
    })


def detail_livre(request, slug):
    livre = get_object_or_404(Livre, slug=slug, disponible=True)
    avis_list = livre.avis.all()
    livres_similaires = Livre.objects.filter(
        categorie=livre.categorie, disponible=True
    ).exclude(pk=livre.pk)[:4]

    avis_form = AvisForm()
    user_a_deja_note = False
    user_favori = False
    user_peut_telecharger = False

    if request.user.is_authenticated:
        user_a_deja_note = AvisLivre.objects.filter(livre=livre, auteur=request.user).exists()
        user_favori = Favori.objects.filter(livre=livre, utilisateur=request.user).exists()

        if livre.est_numerique() and livre.fichier_pdf:
            user_peut_telecharger = TelechargementPDF.objects.filter(
                utilisateur=request.user, livre=livre
            ).exists()

            if not user_peut_telecharger:
                from gestion_commandes.models import LigneCommande
                user_peut_telecharger = LigneCommande.objects.filter(
                    livre=livre,
                    commande__client=request.user,
                    commande__statut="payee"
                ).exists()

        if request.method == "POST" and not user_a_deja_note:
            avis_form = AvisForm(request.POST)
            if avis_form.is_valid():
                avis = avis_form.save(commit=False)
                avis.livre = livre
                avis.auteur = request.user
                avis.save()
                messages.success(request, "Votre avis a été publié.")
                return redirect("detail_livre", slug=slug)

    return render(request, "gestion_livres/detail_livre.html", {
        "livre": livre,
        "avis_list": avis_list,
        "livres_similaires": livres_similaires,
        "avis_form": avis_form,
        "user_a_deja_note": user_a_deja_note,
        "user_favori": user_favori,
        "user_peut_telecharger": user_peut_telecharger,
    })


@login_required
def telecharger_pdf(request, slug):
    livre = get_object_or_404(Livre, slug=slug, disponible=True)

    if not livre.est_numerique() or not livre.fichier_pdf:
        messages.error(request, "Ce livre n'est pas disponible en version numérique.")
        return redirect("detail_livre", slug=slug)

    from gestion_commandes.models import LigneCommande

    a_acces = (
        TelechargementPDF.objects.filter(utilisateur=request.user, livre=livre).exists()
        or LigneCommande.objects.filter(
            livre=livre,
            commande__client=request.user,
            commande__statut="payee"
        ).exists()
        or request.user.is_staff
    )

    if not a_acces:
        messages.warning(request, "Vous devez acheter ce livre pour pouvoir le télécharger.")
        return redirect("detail_livre", slug=slug)

    tel, created = TelechargementPDF.objects.get_or_create(
        utilisateur=request.user, livre=livre
    )
    if not created:
        tel.nombre_telechargements += 1
        tel.save(update_fields=["nombre_telechargements"])

    fichier = livre.fichier_pdf
    if not fichier or not os.path.exists(fichier.path):
        raise Http404("Fichier introuvable.")

    nom_fichier = f"{livre.slug}.pdf"
    response = FileResponse(open(fichier.path, "rb"), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nom_fichier}"'
    return response


@login_required
def toggle_favori(request, slug):
    livre = get_object_or_404(Livre, slug=slug)
    favori, created = Favori.objects.get_or_create(utilisateur=request.user, livre=livre)
    if not created:
        favori.delete()
        messages.info(request, "Retiré de vos favoris.")
    else:
        messages.success(request, "Ajouté à vos favoris.")
    return redirect("detail_livre", slug=slug)


@login_required
def mes_favoris(request):
    favoris = Favori.objects.filter(utilisateur=request.user).select_related("livre")
    return render(request, "gestion_livres/mes_favoris.html", {"favoris": favoris})


@login_required
def mes_telechargements(request):
    from gestion_commandes.models import LigneCommande

    livres_payes_ids = LigneCommande.objects.filter(
        commande__client=request.user,
        commande__statut="payee",
        livre__isnull=False,
        livre__fichier_pdf__isnull=False,
        livre__type_vente__in=["numerique", "les_deux"]
    ).values_list("livre_id", flat=True).distinct()

    livres_numeriques = Livre.objects.filter(
        id__in=livres_payes_ids, disponible=True
    ).select_related("categorie")

    telechargements_map = {t.livre_id: t for t in TelechargementPDF.objects.filter(utilisateur=request.user)}

    livres_avec_info = []
    for livre in livres_numeriques:
        tel = telechargements_map.get(livre.id)
        livres_avec_info.append({
            "livre": livre,
            "nb_telechargements": tel.nombre_telechargements if tel else 0,
            "date_premier": tel.date if tel else None,
        })

    return render(request, "gestion_livres/mes_telechargements.html", {
        "livres_avec_info": livres_avec_info,
    })


def livres_kabiye(request):
    livres = Livre.objects.filter(categorie__slug="livres-kabiye", disponible=True)
    paginator = Paginator(livres, 12)
    livres_page = paginator.get_page(request.GET.get("page", 1))
    return render(request, "gestion_livres/boutique.html", {
        "livres": livres_page,
        "titre_page": "Livres Kabiyè",
        "form": RechercheForm(),
        "categories": Categorie.objects.filter(active=True),
        "total_resultats": livres.count(),
    })
