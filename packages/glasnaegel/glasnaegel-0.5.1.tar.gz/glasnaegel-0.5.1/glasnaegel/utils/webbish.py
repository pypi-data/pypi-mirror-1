# -*- coding: utf-8 -*-

from glashammer.utils import Pagination


def paginated(query, req, url_args=None):
    page = int(req.values.get('page', 1))
    per_page = int(req.values.get('per_page', 15))
    total = query.count()
    url_args = url_args or {}
    pagination = Pagination(req.endpoint, page, per_page, total, url_args)
    offset = (page-1) * per_page
    limit = offset + per_page
    paginated_objects = query[offset:limit]
    return paginated_objects, pagination

