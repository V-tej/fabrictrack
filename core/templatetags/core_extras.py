from django import template

register = template.Library()

@register.filter(name='split')
def split_filter(value, separator):
    """Split a string by separator and return a list — used in activity_log.html."""
    if not value:
        return []
    return [part.strip() for part in str(value).split(separator) if part.strip()]

@register.filter(name='contains')
def contains_filter(value, substring):
    """Return True if substring is found in value."""
    return substring in str(value) if value else False
