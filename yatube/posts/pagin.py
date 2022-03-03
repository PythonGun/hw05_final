from django.conf import settings
from django.core.paginator import Paginator


def paginator_main(request, post_list):
    paginator = Paginator(post_list, settings.PAGE_NUM)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page
