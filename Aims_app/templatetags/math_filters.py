from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        value = Decimal(str(value))
        arg = Decimal(str(arg))
        result = value * arg
        print(f"DEBUG: {value} * {arg} = {result}")  # DEBUG PRINT
        return result
    except (ValueError, TypeError, InvalidOperation) as e:
        print(f"DEBUG ERROR: {e}")
        return 0
