# Based on code by Sean Reifschneider, which was
# based on: http://www.djangosnippets.org/snippets/73/
#
# Modified by Kenneth Lett to use explicite page variable
# rather than context

from django import template

register = template.Library()


@register.inclusion_tag('podmin/pagination.html')
def paginator(page, adjacent_pages=3):

    startPage = max(page.number - adjacent_pages, 1)

    num_pages = page.paginator.num_pages

    if startPage <= 3:
        startPage = 1
    endPage = page.number + adjacent_pages + 1
    if endPage >= num_pages - 1:
        endPage = num_pages + 1
    page_numbers = [n for n in range(startPage, endPage)
                    if n > 0 and n <= num_pages]

    try:
        next = page.next_page_number()
    except:
        next = False

    try:
        previous = page.previous_page_number()
    except:
        previous = False


    page_obj = page
    paginator = page.paginator

    return {
        'page_obj': page_obj,
        'paginator': paginator,
        'page': page.number,
        'pages': num_pages,
        'page_numbers': page_numbers,
        'next': next,
        'previous': previous,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'show_first': 1 not in page_numbers,
        'show_last': num_pages not in page_numbers,
    }
