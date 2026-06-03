from .models import Categorie


def categories_nav(request):
    """Fournit les catégories principales au navbar sur toutes les pages."""
    categories = Categorie.principales()
    notification_count = 0
    if request.user.is_authenticated:
        try:
            from gestion_notifications.models import Notification
            notification_count = Notification.objects.filter(
                utilisateur=request.user, lue=False
            ).count()
        except Exception:
            pass
    return {
        "nav_categories": categories,
        "notification_count": notification_count,
    }
