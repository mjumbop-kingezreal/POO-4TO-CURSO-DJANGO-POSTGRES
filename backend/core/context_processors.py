from .models import MenuItem


def menu_items(request):
    if not request.user.is_authenticated:
        return {'menu_modules': []}
    modules = MenuItem.all_objects.filter(
        parent__isnull=True, is_active=True
    ).order_by('order')
    return {'menu_modules': modules}