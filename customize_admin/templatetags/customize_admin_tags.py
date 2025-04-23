from django import template

register = template.Library()

@register.filter(name='getattr_safe')  # This is the name you'll use in templates
def get_attribute(obj, attr):
    return getattr(obj, attr, '')

@register.filter
def debug_obj(obj):
    return vars(obj)