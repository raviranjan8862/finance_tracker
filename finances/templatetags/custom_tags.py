# finances/templatetags/custom_tags.py

from django import template

register = template.Library()

@register.filter
def month_range(start, end):
    """Returns a range of months as a list."""
    return range(start, end + 1)

@register.filter
def year_range(start, end):
    """Returns a range of years as a list."""
    return range(start, end + 1)
