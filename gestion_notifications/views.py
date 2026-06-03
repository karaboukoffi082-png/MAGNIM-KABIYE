from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification


@login_required
def mes_notifications(request):
    # 1. On récupère le QuerySet (trié par les plus récentes si tu as un champ date)
    # Remplace '-date_creation' par ton vrai champ de date (ex: '-cree_le') s'il existe
    queryset = Notification.objects.filter(utilisateur=request.user).order_by('-id')
    
    # 2. On compte les non lues
    non_lues = queryset.filter(lue=False).count()
    
    # 3. CORRECTION : On transforme en liste pour figer l'état AVANT la mise à jour
    notifications = list(queryset)
    
    # 4. On passe tout à "lu" en base de données pour la prochaine fois
    queryset.filter(lue=False).update(lue=True)
    
    return render(request, "gestion_notifications/notifications.html", {
        "notifications": notifications,
        "non_lues": non_lues,
    })


@login_required
def marquer_lue(request, pk):
    notif = get_object_or_404(Notification, pk=pk, utilisateur=request.user)
    notif.lue = True
    notif.save()
    if notif.lien:
        return redirect(notif.lien)
    return redirect("mes_notifications")


@login_required
def marquer_toutes_lues(request):
    Notification.objects.filter(utilisateur=request.user, lue=False).update(lue=True)
    return redirect("mes_notifications")


@login_required
def count_non_lues(request):
    count = Notification.objects.filter(utilisateur=request.user, lue=False).count()
    return JsonResponse({"count": count})