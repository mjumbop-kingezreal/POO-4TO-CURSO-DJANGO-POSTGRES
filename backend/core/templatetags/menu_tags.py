from django import template

register = template.Library()


@register.filter
def has_access(menu_item, user):
    return menu_item.has_access(user)


@register.filter
def accessible_children(menu_item, user):
    return menu_item.accessible_children(user)