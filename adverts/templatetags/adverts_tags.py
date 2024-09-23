from django import template
from django.db.models import Count

from adverts.models import Category
from adverts.utils import menu

register = template.Library()


@register.simple_tag
def get_menu():
    return menu


@register.inclusion_tag('adverts/list_categories.html')
def show_categories(cat_selected=0):
    cats = Category.objects.filter(posts__is_published=True).annotate(total=Count("posts")).filter(total__gt=0)
    return {'cats': cats, 'cat_selected': cat_selected}
