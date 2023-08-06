# -*- coding: utf-8 -*-
#
#  Copyright (c) 2010 Andrey Mikhaylenko and contributors
#
#  This file is part of Glasnägel.
#
#  Glasnägel is free software under terms of the GNU Lesser General Public
#  License version 3 (LGPLv3) as published by the Free Software Foundation.
#  See the file README for copying conditions.
#

from glashammer.utils import render_response, Response
from glashammer.utils.appliance import Appliance


def render_to(template):
    """
    A view function decorator. Supports both stand-alone views and Appliance
    methods. If the view returns a Response object, it is returned immediately.
    If the view returns a dictionary, the template is rendered with that
    dictionary as the context.

    Usage::

        class Wiki(Appliance):

            @expose('/')
            @render_to('index.html')
            def index(self, request):
                "Displays all available pages"
                return {
                    'pages': Page.query(self.db)
                }

    """
    def _outer(view):
        def _inner(*args, **kwargs):
            result = view(*args, **kwargs)
            if isinstance(result, Response):
                return result
            assert isinstance(result, dict), ('view decorated by render_to must '
                                              'return a dictionary')
            if args and isinstance(args[0], Appliance):
                renderer = args[0].render_response
            else:
                renderer = render_response
            return renderer(template, **result)
        # preserve name and docstring
        for attr in '__name__', '__doc__':
            setattr(_inner, attr, getattr(view, attr))
        return _inner
    return _outer
