from django import template
from django.forms import CheckboxInput, SelectMultiple
import os

register = template.Library()


@register.filter(name='is_checkbox')
def is_checkbox(field):
    return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__

@register.filter(name='is_selectmultiple')
def is_checkbox(field):
    return field.field.widget.__class__.__name__ == SelectMultiple().__class__.__name__

@register.filter(name='filename')
def filename(value):
    return os.path.basename(value)
