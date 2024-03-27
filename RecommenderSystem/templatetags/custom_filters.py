# custom_filters.py

from django import template

register = template.Library()

@register.filter
def split_string(value, delimiter=','):
    """Custom template filter to split a string into a list."""
    return value.split(delimiter)


@register.filter(name='split_list')
def split_list(value, delimiter=','):
    """Custom template filter to split a string or list into a list."""
    if isinstance(value, list):
        return value
    elif isinstance(value, str):
        # Check if the string starts and ends with '[' and ']'
        if value.startswith('[') and value.endswith(']'):
            # Remove '[' and ']' and split the string
            value = value[1:-1]
        # Split the string using the specified delimiter
        values = value.split(delimiter)
        # Strip each value from leading and trailing spaces and quotes
        return [v.strip().strip('\'"') for v in values]
    else:
        return []
    


@register.filter
def split_by_space(value):
    """Custom template filter to split a string by space."""
    return value.split()
