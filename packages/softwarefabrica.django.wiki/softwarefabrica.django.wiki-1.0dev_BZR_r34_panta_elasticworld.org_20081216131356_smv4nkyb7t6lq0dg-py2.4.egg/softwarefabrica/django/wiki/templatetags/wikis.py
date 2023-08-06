from django import template

from softwarefabrica.django.wiki.models import *

register = template.Library()

@register.inclusion_tag('wiki/tags/wikis.html')
def wikis(num = 30):
    wikis = Wiki.objects.order_by('-created')[:num]
    return {
        'wikis': wikis,
    }
