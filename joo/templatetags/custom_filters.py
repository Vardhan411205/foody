from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """Replace all instances of arg[0] with arg[1] in value"""
    old, new = arg.split(',')
    return value.replace(old, new) 