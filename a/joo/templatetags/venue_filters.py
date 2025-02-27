from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string into a list using the specified delimiter"""
    if value:
        return [x.strip() for x in value.split(delimiter)]
    return []

@register.filter
def strip_space(value):
    """Strip whitespace from the beginning and end of a string"""
    if value:
        return value.strip()
    return '' 