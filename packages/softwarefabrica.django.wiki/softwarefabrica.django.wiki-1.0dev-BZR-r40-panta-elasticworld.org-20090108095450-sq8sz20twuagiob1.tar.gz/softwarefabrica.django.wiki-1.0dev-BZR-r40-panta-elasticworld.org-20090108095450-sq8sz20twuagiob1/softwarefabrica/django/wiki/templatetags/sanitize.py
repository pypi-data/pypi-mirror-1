# derived from snippet http://www.djangosnippets.org/snippets/205/

from django import template
from softwarefabrica.django.wiki.sanitize import sanitize_html

register = template.Library()

def sanitize_html_filter(value):
    return sanitize_html(value)

register.filter('santize', sanitize_html_filter)
