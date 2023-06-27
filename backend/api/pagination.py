from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 6

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'response': data,
        })
