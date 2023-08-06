# -*- coding: utf-8 -*-

"""
glasnaegel.utils.appliance
~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2010 Andrey Mikhaylenko
:license: LGPL

An extended version of Glashammer Appliances with support for multiple URLs
pointing to a single view via chained `expose` decorators.
"""

from werkzeug.routing import Rule
from glashammer.utils.appliance import Appliance as BaseAppliance


def expose(url, endpoint=None, **rule_kw):
    def view(f, endpoint=endpoint, rule_kw=rule_kw):
        f.urls = f.urls if hasattr(f, 'urls') else []
        f.urls.append(url)
        if endpoint is None:
            endpoint = f.func_name
        f.endpoint = endpoint
        f.rule_kw = rule_kw
        view.__name__ = f.__name__
        return f
    return view


class Appliance(BaseAppliance):
    def _find_urls(self):
        for name in dir(self):
            attr = getattr(self, name)
            if hasattr(attr, 'urls'):
                yield attr

    def _find_rules(self):
        for method in self._find_urls():
            for url in method.urls:
                yield Rule(url, endpoint=method.endpoint, **method.rule_kw)
