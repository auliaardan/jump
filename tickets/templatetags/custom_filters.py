from django import template

register = template.Library()


@register.filter
def range_filter(value):
    return range(value)


@register.filter
def idr_format(value):
    try:
        value = float(value)
        return "Rp {:,.0f}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value

@register.filter(name='add_class')
def add_class(field, css):
    existing_classes = field.field.widget.attrs.get('class', '')
    if existing_classes:
        new_classes = existing_classes + ' ' + css
    else:
        new_classes = css
    field.field.widget.attrs['class'] = new_classes
    return field