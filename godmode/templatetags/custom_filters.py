from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """Subtracts the arg from value."""
    return value - arg

@register.filter
def add(value, arg):
    """add the arg from value."""
    return (value + arg)
