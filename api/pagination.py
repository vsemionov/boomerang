from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    page_size_query_param = 'size'
    max_page_size = settings.API_MAX_PAGE_SIZE
