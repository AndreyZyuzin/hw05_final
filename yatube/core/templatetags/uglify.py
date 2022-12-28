from django import template

register = template.Library()


@register.filter
def uglify(text):
    return ''.join(
        [c.lower() if i % 2 else c.upper() for i, c in enumerate(text)])
