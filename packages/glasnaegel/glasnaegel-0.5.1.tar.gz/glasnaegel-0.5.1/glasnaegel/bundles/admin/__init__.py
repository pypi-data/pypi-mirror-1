# -*- coding: utf-8 -*-

"""
Glashammer-powered administrative interface for PyModels.
"""

# gh
from glashammer.utils import Response, get_app, redirect_to
#from glashammer.bundles.i18n import setup_i18n, _

# 3rd-party
from glasnaegel.decorators import render_to
from glasnaegel.bundles.models import setup_models, storage
from glasnaegel.bundles.auth import setup_auth, login_required
from glasnaegel.utils import Appliance, expose, paginated
from pymodels.utils.forms import model_form_factory



class AdminSite(Appliance):

    _registered_models = {}
    _urls_for_models = {}
    _excluded_names = {}

    def setup_appliance(self, app):
        app.add_setup(setup_auth)
        #app.add_setup(setup_i18n)
        app.add_setup(setup_models)

    @classmethod
    def register(cls, model, namespace='main', url=None, exclude=None):
        """
        :param model: a PyModels model
        :param namespace: a short string that will be part of the URL. Default
            is "main".
        :param url: a function that gets a model instance and returns an URL
        """
        # TODO: model should provide a slugified version of its name itself
        name = model.__name__.lower()
        cls._registered_models.setdefault(namespace, {})[name] = model
        cls._urls_for_models[model] = url
        cls._excluded_names[model] = exclude

    def _get_model(self, namespace, name):
        if namespace not in self._registered_models:
            raise NameError('There is no registered namespace "%s"' % namespace)
        try:
            return self._registered_models[namespace][name]
        except KeyError:
            raise NameError('"%s" is not a registered model in namespace %s.' %
                            (name, namespace))

    def _get_excluded_names(self, model):
        return self._excluded_names[model] or []

    def _get_url_for_object(self, obj):
        if not obj.pk:
            return
        model = type(obj)
        f = self._urls_for_models[model]
        return f(obj) if f else None

    #-- VIEWS ------------------------------------------------------------------

    @expose('/')
    @render_to('admin/index.html')
    def index(self, req):
        return {
            'namespaces': self._registered_models,
        }

    @expose('/<string:namespace>/<string:model_name>/')
    # TODO: @login_required
    @render_to('admin/object_list.html')
    def object_list(self, req, namespace, model_name):
        model = self._get_model(namespace, model_name)
        query = model.objects(storage)
        pagin_args =  {'namespace': namespace, 'model_name': model_name}
        objects, pagination = paginated(query, req, pagin_args)
        return {
            'namespace': namespace,
            'query': query,
            'objects': objects,
            'pagination': pagination,
        }

    @expose('/<string:namespace>/<string:model_name>/<string:pk>/')
    @expose('/<string:namespace>/<string:model_name>/add/')
    # TODO: @login_required
    @render_to('admin/object_detail.html')
    def object_detail(self, req, namespace, model_name, pk=None):
        model = self._get_model(namespace, model_name)
        if pk:
            obj = storage.get(model, pk)
            creating = False
        else:
            obj = model()
            creating = True
        ModelForm = model_form_factory(model, storage)
        form = ModelForm(req.form, obj)
        
        for name in self._get_excluded_names(model):
            del form[name]
        
        message = None
        if req.method == 'POST' and form.validate():
            form.populate_obj(obj)
            obj.save(storage)    # storage can be omitted if not creating obj
            message = u'%s has been saved.' % obj.__class__.__name__
            if creating:
                # redirect to the same view but change URL
                # from ".../my_model/add/" to
                # to the editing URL ".../my_model/123/"
                return redirect_to('adminsite/object_detail',
                                   namespace=namespace, model_name=model_name,
                                   pk=obj.pk)
        url = self._get_url_for_object(obj)
        return {
            'object': obj,
            'object_url': url,
            'form': form,
            'message': message,
        }


