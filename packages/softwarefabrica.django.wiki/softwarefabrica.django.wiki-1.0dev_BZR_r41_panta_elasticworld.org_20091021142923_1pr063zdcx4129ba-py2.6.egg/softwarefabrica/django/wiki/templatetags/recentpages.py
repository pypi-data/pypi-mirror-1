from django import template
import datetime

from softwarefabrica.django.wiki.models import *

register = template.Library()

@register.inclusion_tag('wiki/tags/last_modified_pages.html')
def last_modified_pages(wiki = None, num = 10):
    wikiname = None
    if type(wiki) == type(Wiki):
        wikiname = wiki.name
    elif (type(wiki) == type('')) or type(wiki) == type(u''):
        wikiname = wiki
        wiki = Wiki.objects.get(name = wikiname)
    if wiki:
        pages = Page.objects.filter(wiki = wiki).order_by('-modified')[:num]
    else:
        pages = Page.objects.order_by('-modified', 'wiki')[:num]
    return {
        'wiki': wiki,
        'pages': pages,
    }
