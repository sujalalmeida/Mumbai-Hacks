from django import template
import math

register = template.Library()

@register.filter(name='abs')
def absolute_value(value):
    """Return the absolute value of a number."""
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return value 