from django import template

register = template.Library()


@register.filter
def rupiah(value):
    """
    Format number as Indonesian Rupiah currency.
    Example: 80000 -> "Rp 80.000"
    """
    try:
        # Convert to int if it's a string or decimal
        if isinstance(value, str):
            value = int(float(value))
        else:
            value = int(value)
        
        # Format with dot separators
        formatted = "{:,}".format(value).replace(",", ".")
        return f"Rp {formatted}"
    except (ValueError, TypeError):
        return "Rp 0"


@register.filter
def rupiah_plain(value):
    """
    Format number as Indonesian Rupiah without 'Rp' prefix.
    Example: 80000 -> "80.000"
    """
    try:
        # Convert to int if it's a string or decimal
        if isinstance(value, str):
            value = int(float(value))
        else:
            value = int(value)
        
        # Format with dot separators
        formatted = "{:,}".format(value).replace(",", ".")
        return formatted
    except (ValueError, TypeError):
        return "0"
