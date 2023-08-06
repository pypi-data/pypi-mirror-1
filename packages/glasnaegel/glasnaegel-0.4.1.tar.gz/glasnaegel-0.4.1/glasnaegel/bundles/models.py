# -*- coding: utf-8 -*-
"""
    PyModels bundle for Glashammer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2010 by Andrey Mikhaylenko
    :license: LGPL
"""

# gh
from glashammer.utils import get_app

# 3rd-party
from pymodels import get_storage


__all__ = ['setup_models', 'storage']

DEFAULT_SETTINGS = {
    'backend': 'pymodels.backends.tokyo_tyrant',
    'host': 'localhost',
    'port': 1978,
}


class StorageProxy(object):
    """
    Syntactic sugar for get_db(). Usage::

        from bundles.models import storage

        def some_view(request):
            return Response(Page.query(storage))

    ...which is just another way to write::

        from glashammer.utils import get_app

        def some_view(request):
            app = get_app()
            return Response(Page.query(app.models_db))
    """
    def __getattr__(self, name):
        return getattr(get_app().models_db, name)

storage = StorageProxy()


def setup_models(app):
    """
    Setup the application to use PyModels.
    """

    app.add_config_var('models/storage', dict, DEFAULT_SETTINGS)

    conf = app.cfg['models/storage']

    app.models_db = get_storage(conf)
