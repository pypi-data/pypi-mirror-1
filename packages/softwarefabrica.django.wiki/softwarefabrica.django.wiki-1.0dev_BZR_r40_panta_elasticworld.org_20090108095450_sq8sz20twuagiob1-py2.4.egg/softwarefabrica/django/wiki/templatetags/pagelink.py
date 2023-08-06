from django import template

from softwarefabrica.django.wiki.models import *

register = template.Library()

@register.inclusion_tag('wiki/tags/pagelink.html')
def pagelink(page, no_terminal = 'n'):
    """
    Return the full hierarchical 'name' for a page, with subcompontents
    turned into links.
    """
    no_terminal = no_terminal.lower()[0] in ('t', 'y', '1')

    wiki = page.wiki

    chain = []
    p = page
    while p is not None:
        chain.append(p)
        p = p.parent
    chain.reverse()
    return {
        'wiki': wiki,
        'chain': chain,
        'no_terminal': no_terminal,
        'do_terminal': (not no_terminal),
    }
