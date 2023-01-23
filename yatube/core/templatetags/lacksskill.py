from django import template

register = template.Library()


@register.filter
def lacksskill(value: int) -> int:
    if value < 0:
        return 100
    if value > 100:
        return 0
    return 100 - value
