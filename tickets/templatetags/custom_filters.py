from django import template

register = template.Library()


@register.filter
def range_filter(value):
    return range(value)


@register.filter
def idr_format(value):
    try:
        value = int(value)
        return f"Rp {value:,}".replace(",", ".")
    except (ValueError, TypeError):
        return value
