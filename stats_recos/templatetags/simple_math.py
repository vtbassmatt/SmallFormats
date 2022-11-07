from django import template

register = template.Library()


@register.filter
def percent_of(numerator, denominator):
    if float(denominator) == 0:
        return "---%"
    return str(round(float(numerator) / float(denominator) * 100, 1)) + "%"

@register.filter
def plus(value, addend):
    try:
        return value + addend
    except TypeError:
        return '---'
