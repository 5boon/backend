from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
import urllib.parse as urlparse
from urllib.parse import parse_qs


class CustomCursorPagination(CursorPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    ordering = '-id'

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_cursor(self.get_next_link()),
            'previous': self.get_cursor(self.get_previous_link()),
            'results': data
        })

    @staticmethod
    def get_cursor(cursor_link: str):
        parsed = urlparse.urlparse(cursor_link)
        cursor = parse_qs(parsed.query).get('cursor')

        if cursor:
            return cursor[0]
        else:
            return None
