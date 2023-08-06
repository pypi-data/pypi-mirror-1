# wiki template filter
# Copyright (C) 2006-2008 Marco Pantaleoni. All rights reserved.
#
# markdown + rk:art "ContentBBcode" template filter
# see ../cbcparser.py
# see http://code.djangoproject.com/wiki/contentBBCode_parser

from django import template
from django.utils.safestring import mark_safe

from softwarefabrica.django.wiki.models import *
from softwarefabrica.django.wiki.wikiparse import wikiparse

register = template.Library()

def wiki(value, page=None, makesafe=True): # Only one argument.
    assert isinstance(value, PageContent)

    (text, linked_pages) = wikiparse(value, makesafe)
    return text
wiki.is_safe = True
register.filter('wiki', wiki)
