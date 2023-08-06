from django import template
from quran.models import *

register = template.Library()

@register.filter(name='translate')
def translate(value, arg=Translation.get(id=1)):
    """
    Display the translation for the given aya
    """
    return TranslatedAya.get(aya=aya, translation=translation)