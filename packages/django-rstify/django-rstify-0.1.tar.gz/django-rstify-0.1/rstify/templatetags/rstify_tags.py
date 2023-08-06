from django import template
from django.utils.safestring import mark_safe
from rstify.utils import rstify

register = template.Library()

@register.filter(name='rstify')
def do_rstify(text, initial_header_level=1):
    return mark_safe(rstify(text, initial_header_level=int(initial_header_level)))