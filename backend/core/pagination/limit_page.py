from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class LimitPagePagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'limit'  # <- вот тут ты получаешь limit
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
