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


@register.inclusion_tag('partials/_pagination.html', takes_context=True)
def render_pagination(context, page_obj=None):
    request = context.get('request')
    page_obj = page_obj or context.get('page_obj')

    if not page_obj:
        return {'show_pagination': False}

    query_params = request.GET.copy() if request else None
    if query_params is not None and 'page' in query_params:
        query_params.pop('page')
    query_string = query_params.urlencode() if query_params else ''

    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages

    page_numbers = []
    if total_pages <= 7:
        page_numbers = list(range(1, total_pages + 1))
    else:
        page_numbers = [1]
        start_page = max(current_page - 2, 2)
        end_page = min(current_page + 2, total_pages - 1)

        if start_page > 2:
            page_numbers.append('ellipsis-left')

        page_numbers.extend(range(start_page, end_page + 1))

        if end_page < total_pages - 1:
            page_numbers.append('ellipsis-right')

        page_numbers.append(total_pages)

    return {
        'show_pagination': True,
        'page_obj': page_obj,
        'query_string': query_string,
        'page_numbers': page_numbers,
        'start_index': page_obj.start_index(),
        'end_index': page_obj.end_index(),
        'total_count': page_obj.paginator.count,
    }
