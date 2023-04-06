from django import template
import locale

from django.conf import settings

register = template.Library()

@register.filter
def number_format(value, decimals=0):
    try:
        locale.setlocale(locale.LC_ALL, settings.LANGUAGE_CODE)  # Utiliza la configuración regional de settings.py
        formatted_value = locale.format_string(f'%.{decimals}f', float(value), grouping=True)
        return formatted_value
    except ValueError:
        return value
