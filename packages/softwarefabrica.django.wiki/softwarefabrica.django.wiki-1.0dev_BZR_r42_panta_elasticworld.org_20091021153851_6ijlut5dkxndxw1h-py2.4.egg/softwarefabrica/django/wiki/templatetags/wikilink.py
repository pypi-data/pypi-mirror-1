from django import template

from softwarefabrica.django.wiki.models import *

register = template.Library()

@register.inclusion_tag('wiki/tags/wikilink.html')
def wikilink(wiki, no_terminal = 'n'):
    """
    Return the full hierarchical 'name' for a wiki, with subcompontents
    turned into links.
    """
    no_terminal = no_terminal.lower()[0] in ('t', 'y', '1')
    chain = []
    w = wiki
    while w is not None:
        chain.append(w)
        w = w.parent
    chain.reverse()
    return {
        'chain': chain,
        'no_terminal': no_terminal,
        'do_terminal': (not no_terminal),
    }
