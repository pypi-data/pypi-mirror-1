# crud.py
#
# Copyright (C) 2007-2008 Marco Pantaleoni. All rights reserved
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
CRUD functionality.
"""

from django.template import RequestContext, loader
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.xheaders import populate_xheaders
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.utils.translation import ugettext
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator, InvalidPage
from django.views.generic import GenericViewError

from django.utils.encoding import force_unicode, smart_str
from django.utils.safestring import mark_safe
from django import forms
from django.forms.forms import BoundField

from softwarefabrica.django.forms.extended import Form, ModelForm, modelform_factory, extended_formfield_cb

import logging

# CONTEXT_POPUP_VARIABLE is added to the context with the value of request GET POPUP_VARIABLE
# this allows more painless handling of popup windows (eg. for SelectPopupWidget, RelatedItemWidget, ...)
POPUP_VARIABLE = '_popup'
CONTEXT_POPUP_VARIABLE = 'is_popup'

def string_to_bool(s):
    if s in (False, 0, '0', 'n', 'no', 'false', 'False', 'f'):
        return False
    return True

def bool_to_string(v):
    if v:
        return '1'
    return '0'

# ------------------------------------------------------------------------
#   OBJECT-ORIENTED GENERIC VIEWS
# ------------------------------------------------------------------------

class ViewCall(object):
    """Represent a view call (keeping all parameters passed to the view)."""
    def __init__(self, request, view, view_args=None, view_kwargs=None, *args, **kwargs):
        assert isinstance(request, HttpRequest)
        assert isinstance(view, View)
        view_args   = tuple(view_args or ())
        view_kwargs = view_kwargs or {}
        if args:
            view_args = tuple(args) + tuple(view_args)
        if kwargs:
            view_kwargs.update(kwargs)
        self.view_args   = view_args
        self.view_kwargs = view_kwargs

        self.request              = request
        self.response             = None
        self.view                 = view

        # `c_NAME` are fields determined during the handling of the view call
        self.c_context         = None
        self.c_template_name   = None
        self.c_template_loader = None
        self.c_template        = None
        self.c_model           = None
        self.c_form_class      = None
        self.c_form_kwargs     = None
        self.c_form            = None
        self.c_instance        = None
        self.c_queryset        = None
        self.c_paginator       = None
        self.c_page            = None # request page (number string or 'last' or None)
        self.c_page_num        = None # page number
        self.c_page_obj        = None
        self.c_object_list     = None # objects on current page
        self.c_is_paginated    = None

    def __repr__(self):
        return "<ViewCall view:%s.%s args:%s kwargs:%s>" % (self.view.__class__.__module__,
                                                            self.view.__class__.__name__,
                                                            repr(self.view_args),
                                                            repr(self.view_kwargs))

    def pre_call(self):
        """Called at the beginning of a view processing."""
        return self

    def _get_view_kwarg(self, argname, attr_name=None, viewclass_attr_name=None, default=None):
        attr_name           = attr_name or argname
        viewclass_attr_name = viewclass_attr_name or attr_name
        i_default = default
        if hasattr(self.view, attr_name):
            i_default = getattr(self.view, attr_name)
        elif hasattr(self.view.__class__, viewclass_attr_name):
            i_default = getattr(self.view.__class__, viewclass_attr_name)
        elif hasattr(self.view.__class__, viewclass_attr_name.upper()):
            i_default = getattr(self.view.__class__, viewclass_attr_name.upper())
        r = self.view_kwargs.get(argname, i_default)
        if (argname == 'extra_context') and (not r):
            r = {}
        return r

    def __getattr__(self, name):
        return self._get_view_kwarg(name)

    def __getitem__(self, name):
        return self._get_view_kwarg(name)

    def __setitem__(self, name, value):
        self.view_args[name] = value

    def __iter__(self):
        return self.view_args.__iter__()

class View(object):
    """
    Object-oriented base view.
    """ 

    TEMPLATE_NAME      = None
    TEMPLATE_LOADER    = loader
    EXTRA_CONTEXT      = {}
    LOGIN_REQUIRED     = False
    CONTEXT_PROCESSORS = None

    NOT_AUTHORIZED_MSG = u"Access not authorized."

    VIEWCALL_CLASS = ViewCall

    CACHE_TEMPLATE     = True
    _TEMPLATE_CACHE    = {}

    __name__ = 'View'

    def __init__(self, template_name = None, template_loader = None,
                 extra_context = None, login_required = None,
                 context_processors = None, cache_template = None,
                 viewcall_class = None):
        """
        Object-oriented base django view.

        Constructor arguments:

        ``template_name``
            name of template to use, or list of templates.

        ``template_loader``
            template loader to use (defaults to django.template.loader).

        ``extra_context``
            dictionary of items and/or callables to add to template
            context.

        ``login_required``
            True if login is required by this view (defaults to False).

        ``context_processors``
            context processors passed to RequestContext() (defaults to None).

        View call arguments:
        """

        self.template_name      = template_name or self.TEMPLATE_NAME
        self.template_loader    = template_loader or self.TEMPLATE_LOADER
        self.extra_context      = extra_context or self.EXTRA_CONTEXT or {}
        if login_required is not None:
            self.login_required = login_required
        else:
            self.login_required = self.LOGIN_REQUIRED
        self.context_processors = context_processors or self.CONTEXT_PROCESSORS
        self.viewcall_class     = viewcall_class or self.VIEWCALL_CLASS

        self.cache_template = cache_template or self.CACHE_TEMPLATE
        self.template_cache = self._TEMPLATE_CACHE

    def __call__(self, request, *args, **kwargs):
        """
        Arguments:

        ``request``
            The HttpRequest object.
        """

        vcall = self.viewcall_class(request, self, args, kwargs)
        assert isinstance(vcall, ViewCall)

        self.pre_call(vcall, request)

        extra_context      = vcall.extra_context or {}
        login_required     = vcall.login_required
        if login_required is None:
            login_required = self.login_required

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(vcall, request)
        if not self.check_auth(vcall, request):
            return self.perm_negated(vcall, request)
        if extra_context is None: extra_context = {}
        self.apply_extra_context(vcall, extra_context, self.extra_context)
        c = self.get_context(vcall, request, {})
        self.apply_extra_context(vcall, c, extra_context)
        self._populate_context(vcall, request)
        self.populate_context(vcall, request)
        self.get_template(vcall)
        return self.get_response(vcall)

    def pre_call(self, vcall, request):
        """
        Override in derived classes to customize.
        """
        assert isinstance(vcall, ViewCall)
        vcall.pre_call()
        return self

    def merge_dict(self, target_dict, added_dict):
        """
        Add items from added_dict dict to the given target_dict dict,
        calling any callables in added_dict.  Return the updated target_dict dict.
        """
        added_dict = added_dict or {}
        for key, value in added_dict.iteritems():
            if callable(value):
                target_dict[key] = value()
            else:
                target_dict[key] = value
        return target_dict

    def apply_extra_context(self, vcall, context, extra_context = None):
        assert isinstance(vcall, ViewCall)
        # TODO: add vcall.extra_context ?
        logging.warn("TODO: add vcall.extra_context in apply_extra_context() ?")
        extra_context = extra_context or self.extra_context
        return self.merge_dict(context, extra_context)

    def _populate_context(self, vcall, request):
        """
        Used by the generic views implementations to populate context.
        Not really meant to be overridden, use ``populate_context`` for
        that.
        """
        return self

    def populate_context(self, vcall, request):
        """
        Override to add additional contents to the context.
        """
        return self

    def get_template(self, vcall, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        assert isinstance(vcall, ViewCall)
        template_name   = template_name or vcall.c_template_name or vcall.template_name or self.template_name
        template_loader = template_loader or vcall.c_template_loader or vcall.template_loader or self.template_loader
        vcall.c_template_name   = template_name
        vcall.c_template_loader = template_loader
        if isinstance(template_name, (list, tuple)):
            t_id = tuple(template_name)
        else:
            t_id = template_name
        if self.cache_template and (t_id in self.template_cache):
            tpl = self.template_cache[t_id]
            vcall.c_template = tpl
            return tpl
        if isinstance(template_name, (list, tuple)):
            tpl = template_loader.select_template(template_name)
            if self.cache_template:
                self.template_cache[t_id] = tpl
            vcall.c_template = tpl
            return tpl
        else:
            tpl = template_loader.get_template(template_name)
            if self.cache_template:
                self.template_cache[t_id] = tpl
            vcall.c_template = tpl
            return tpl
        return None

    def get_context(self, vcall, request, dictionary = {}, context_processors = None):
        """
        Return a context instance with data in ``dictionary``.
        """
        assert isinstance(vcall, ViewCall)
        context_processors = context_processors or vcall.context_processors or self.context_processors
        context = RequestContext(request, dictionary, context_processors)
        vcall.c_context = context
        return context

    def get_response(self, vcall, template = None, context_instance = None, mimetype = None):
        """
        Return a HttpResponse object based on given request, template,
        and context.
        """
        assert isinstance(vcall, ViewCall)
        template         = template or vcall.c_template
        context_instance = context_instance or vcall.c_context
        mimetype         = mimetype or vcall.mimetype
        if mimetype is not None:
            response = HttpResponse(template.render(context_instance), mimetype = mimetype)
        else:
            response = HttpResponse(template.render(context_instance))
        vcall.response = response
        return response

    def populate_xheaders(self, vcall, request, response, model, object_id):
        assert isinstance(vcall, ViewCall)
        populate_xheaders(request, response, model, object_id)
        return response

    def redirect_to_login(self, vcall, request):
        assert isinstance(vcall, ViewCall)
        return redirect_to_login(request.path)

    def check_auth(self, vcall, request, queryset = None, instance = None, model = None, *args, **kwargs):
        """
        Override in derived classes to perform auth/perm checks.
        """
        assert isinstance(vcall, ViewCall)
        return True

    def perm_negated(self, vcall, request, queryset = None, instance = None, model = None, *args, **kwargs):
        """
        Override in derived classes to alter the unauthorized response behaviour.
        """
        assert isinstance(vcall, ViewCall)
        return HttpResponseForbidden(ugettext(self.NOT_AUTHORIZED_MSG))

class GenericView(View):
    # defaults
    MODEL = None
    FIELDS = None
    EXCLUDE = None
    FIELDORDER = None
    FORMFIELD_CALLBACK = None
    FORMBASE = ModelForm
    FORMCLASS = None

    VIEWCALL_CLASS = ViewCall

    __name__ = 'GenericView'

    def __init__(self, model = None, form_class = None,
                 template_name = None, template_loader = None,
                 extra_context = None, login_required = None, context_processors = None,
                 fields = None, exclude = None, fieldorder = None, formfield_callback = None, formbase = None,
                 viewcall_class = None):
        """
        Arguments:

        ``model``
            Model type to create (either this or form_class is required)

        ``form_class``
            ModelForm subclass to use (either this or model is required)
        """

        super(GenericView, self).__init__(template_name, template_loader, extra_context, login_required, context_processors)
        self.fields             = fields or self.FIELDS
        self.exclude            = exclude or self.EXCLUDE
        self.fieldorder         = fieldorder or self.FIELDORDER
        self.formfield_callback = formfield_callback or self.FORMFIELD_CALLBACK
        self.formbase           = formbase or self.FORMBASE

        self.model              = model or self.MODEL
        self.form_class         = form_class or self.FORMCLASS
        self.viewcall_class     = viewcall_class or self.VIEWCALL_CLASS

    def __call__(self, request, *args, **kwargs):
        vcall = self.viewcall_class(request, self, args, kwargs)
        assert isinstance(vcall, ViewCall)

        self.pre_call(vcall, request)

        model              = vcall.model or self.model
        extra_context      = vcall.extra_context or {}
        login_required     = vcall.login_required
        if login_required is None:
            login_required = self.login_required

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(vcall, request)
        if not self.check_auth(vcall, request, model = model):
            return self.perm_negated(vcall, request, model = model)

        if extra_context is None: extra_context = {}

        vcall.c_model = vcall.model
        self.get_model_and_form_class(vcall)
        form = self.get_form(vcall)

        self.apply_extra_context(vcall, extra_context, self.extra_context)
        c = self.get_context(vcall, request, {'form': vcall.c_form})
        self.apply_extra_context(vcall, c, extra_context)
        self._populate_context(vcall, request)
        self.populate_context(vcall, request)
        self.get_template(vcall)
        return self.get_response(vcall)

    def _populate_context(self, vcall, request, model = None, obj = None, template_object_name = None):
        assert isinstance(vcall, ViewCall)
        super(GenericView, self)._populate_context(vcall, request)
        context              = vcall.c_context
        model                = model or vcall.c_model or vcall.model
        obj                  = obj or vcall.c_instance
        template_object_name = template_object_name or vcall.template_object_name or 'object'
        is_popup             = string_to_bool(request.GET.get(POPUP_VARIABLE, False))
        context[CONTEXT_POPUP_VARIABLE] = is_popup
        context['request']      = request
        context['viewcall']     = vcall
        context['full_path']    = request.get_full_path()       # "/music/bands/the_beatles/?print=true"
        context['URI']          = request.build_absolute_uri()  # "http://.../music/bands/the_beatles/?print=true"
        context['GET']          = request.GET
        context['POST']         = request.POST
        context['query_string'] = request.GET.urlencode()
        context['model']        = model
        if model is not None:
            opts                 = model._meta
            verbose_name         = force_unicode(opts.verbose_name)
            object_name          = force_unicode(opts.object_name.lower())
            context['meta']         = opts
            context['verbose_name'] = mark_safe(verbose_name)
            context['object_name']  = mark_safe(object_name)
        if obj is not None:
            context[template_object_name] = obj
            context[template_object_name + '_id'] = getattr(obj, obj._meta.pk.attname)
        return self

    def get_template(self, vcall, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        assert isinstance(vcall, ViewCall)
        model           = vcall.c_model or vcall.model
        template_name   = template_name or vcall.c_template_name or vcall.template_name or self.template_name
        template_loader = template_loader or vcall.c_template_loader or vcall.template_loader or self.template_loader
        vcall.c_template_name   = template_name
        vcall.c_template_loader = template_loader

        app_label   = model._meta.app_label
        object_name = model._meta.object_name.lower()
        template_name = template_name or ("%s/%s_form.html" % (app_label, object_name),
                                          "%s/object_form.html" % app_label,
                                          "%s_form.html" % object_name,
                                          "object_form.html")
        vcall.c_template_name = template_name
        return super(GenericView, self).get_template(vcall,
                                                     template_name = template_name,
                                                     template_loader = template_loader)

    def get_model_and_form_class(self, vcall, model = None, form_class = None,
                                 fields = None, exclude = None,
                                 formfield_callback = None,
                                 formbase = None, popup_models = None):
        """
        Returns a model and form class based on the model and form_class
        parameters that were passed to the generic view.

        These values will be set in the passed ViewCall as the `c_model` and
        `c_form_class` fields.

        If ``form_class`` is given then its associated model will be returned along
        with ``form_class`` itself.  Otherwise, if ``model`` is given, ``model``
        itself will be returned along with a ``ModelForm`` class created from
        ``model``.

        ``form`` is the form base class used (passed to ModelFormMetaclass to create
        the final form class).
        """

        assert isinstance(vcall, ViewCall)

        default_formfield_cb = lambda f, pm=vcall.popup_models, cb=extended_formfield_cb: cb(f, popup_models=pm)

        model              = model or vcall.model or self.model
        form_class         = form_class or vcall.form_class or self.form_class
        fields             = fields or vcall.fields or self.fields
        exclude            = exclude or vcall.exclude or self.exclude
        formfield_callback = formfield_callback or vcall.formfield_callback or default_formfield_cb
        formbase           = formbase or vcall.formbase or ModelForm
        popup_models       = popup_models or vcall.popup_models

        if form_class and hasattr(form_class, '_meta') and hasattr(form_class._meta, 'model'):
            vcall.c_model      = form_class._meta.model
            vcall.c_form_class = form_class
            return self
        if model:
            form_class = modelform_factory(model, form=formbase,
                                           fields=fields, exclude=exclude,
                                           formfield_callback=formfield_callback)
            vcall.c_model      = model
            vcall.c_form_class = form_class
            return self
        raise GenericViewError("%s view must be called with either a model or"
                               " form_class argument." % (self.__class__.__name__,))

    def get_form_kwargs(self, vcall, fieldorder = None, initial = None):
        """
        Get dictionary of arguments to construct the appropriate
        ``form_class`` instance.
        """
        assert isinstance(vcall, ViewCall)
        request = vcall.request
        fieldorder   = fieldorder or vcall.fieldorder or self.fieldorder
        form_initial = initial or vcall.form_initial

        form_kwargs = {}
        if request.method == 'POST':
            form_kwargs = {'data': request.POST, 'files': request.FILES}
            if fieldorder:
                form_kwargs['fieldorder'] = fieldorder
            if form_initial:
                form_kwargs['initial'] = form_initial
        vcall.c_form_kwargs = form_kwargs
        return form_kwargs

    def get_form(self, vcall, form_class = None, fieldorder = None, initial = None):
        """
        Return the appropriate ``form_class`` instance based on the
        ``request``.
        """
        assert isinstance(vcall, ViewCall)
        form_class  = form_class or vcall.c_form_class or self.form_class
        form_kwargs = self.get_form_kwargs(vcall, fieldorder, initial)
        vcall.c_form_kwargs = form_kwargs
        vcall.c_form        = form_class(**form_kwargs)
        return vcall.c_form

    def pre_save_instance(self, vcall, obj, form):
        """
        Called before saving a model instance.
        Override in derived classes to modify the object just before saving it
        to the db.
        """
        return obj

    def post_save_instance(self, vcall, obj, form):
        """
        Called after saving a model instance.
        Override in derived classes to implement custom behaviour.
        """
        return self

    def instance_save_args(self, vcall, obj, form):
        """
        Return a tuple (args, kwargs) of parameters for ``obj.save()`` in
        ``save_instance``, or None.
        Override in derived classes to pass additional parameters to ``obj.save()``.
        """
        return None

    def save_instance(self, vcall, obj, form):
        """
        Save and return model instance.
        """
        assert isinstance(vcall, ViewCall)
        n_obj = self.pre_save_instance(vcall, obj, form)
        if n_obj is not None:
            obj = n_obj
        vcall.c_instance = obj
        save_args = self.instance_save_args(vcall, obj, form)
        if save_args is not None:
            (s_args, s_kwargs) = save_args
            obj.save(*s_args, **s_kwargs)
        else:
            obj.save()
        if form:
            self.save_m2m(vcall, form)
        self.post_save_instance(vcall, obj, form)
        # TODO: return vcall.c_instance ?
        logging.warn("TODO: return vcall.c_instance from save_instance() ?")
        return obj

    def save_m2m(self, vcall, form):
        """
        Save the many-to-many related data.
        """
        assert isinstance(vcall, ViewCall)
        form.save_m2m()
        return self

    def pre_delete_instance(self, vcall, obj):
        """
        Called before deleting a model instance.
        Override in derived classes to implement custom behaviour.
        """
        return obj

    def post_delete_instance(self, vcall):
        """
        Called after deleting a model instance.
        Override in derived classes to implement custom behaviour.
        """
        return self

    def delete_instance(self, vcall, obj):
        """
        Delete the given model instance.
        """
        assert isinstance(vcall, ViewCall)
        self.pre_delete_instance(vcall, obj)
        obj.delete()
        self.post_delete_instance(vcall)
        return self

    def save_form(self, vcall, form):
        """
        Save form, returning saved object.
        """
        assert isinstance(vcall, ViewCall)
        instance = form.save(commit=False)
        vcall.c_instance = instance
        return self.save_instance(vcall, instance, form)


class CreateObjectView(GenericView):
    """
    Generic object-creation view.

    Templates: ``<app_label>/<model_name>_create.html``
               ``<app_label>/object_create.html``
               ``<model_name>_create.html``
               ``object_create.html``
               ``common/object_create.html``
               ``<app_label>/<model_name>_edit.html``
               ``<app_label>/object_edit.html``
               ``<model_name>_edit.html``
               ``object_edit.html``
               ``common/object_edit.html``
               ``<app_label>/<model_name>_form.html``
               ``<app_label>/object_form.html``
               ``<model_name>_form.html``
               ``object_form.html``

    Constructor arguments:

        same as in GenericView, and additionally:

        ``post_save_redirect``
            URL to redirect to after successful object save. If
            post_save_redirect is None or an empty string, default is
            to send to the instances get_absolute_url method.

    View call arguments:

        same as in GenericView, and additionally:

        ``model``
            Model type to create (either this or form_class is
            required)

        ``form_class``
            ModelForm subclass to use (either this or model is
            required)

        ``post_save_redirect``

        ``popup_models``
            List of models for which a UI element with buttons for popup selection
            should be used.

    Context:
        model:
            Model of object to be created.
        meta:
            Meta information from the model.
        verbose_name:
            Object verbose name (model._meta.verbose_name).
        object_name:
            Object name (model._meta.object_name.lower()).
        form
            the form for the object
    """

    POST_SAVE_REDIRECT = None
    POPUP_MODELS = None

    __name__ = 'CreateObjectView'

    def __init__(self, post_save_redirect = None, *args, **kwargs):
        popup_models = kwargs.pop('popup_models', self.POPUP_MODELS)
        super(CreateObjectView, self).__init__(*args, **kwargs)
        self.post_save_redirect = post_save_redirect or self.POST_SAVE_REDIRECT
        self.popup_models = popup_models or self.POPUP_MODELS

    #def __call__(self, request, model = None, form_class = None,
    #             template_name = None, template_loader = None, extra_context = {},
    #             post_save_redirect = None,
    #             login_required = None, context_processors = None,
    #             fields = None, exclude = None, fieldorder = None,
    #             formfield_callback = None, formbase = None, form_initial = None, popup_models = None):
    def __call__(self, request, *args, **kwargs):
        vcall = self.viewcall_class(request, self, args, kwargs)
        assert isinstance(vcall, ViewCall)

        self.pre_call(vcall, request)

        model              = vcall.model or self.model
        extra_context      = vcall.extra_context or {}
        login_required     = vcall.login_required
        if login_required is None:
            login_required = self.login_required

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(vcall, request)
        if not self.check_auth(vcall, request, model = model):
            return self.perm_negated(vcall, request, model = model)
        if extra_context is None: extra_context = {}

        vcall.c_model = vcall.model
        self.get_model_and_form_class(vcall)
        form = self.get_form(vcall)

        if request.method == 'POST' and form.is_valid():
            new_object = self.save_form(vcall, form)
            if request.user.is_authenticated():
                request.user.message_set.create(message=ugettext("The %(verbose_name)s was created successfully.") % {"verbose_name": vcall.c_model._meta.verbose_name})
            assert vcall.c_instance == new_object
            return self.get_redirect(vcall, request)

        self.apply_extra_context(vcall, extra_context, self.extra_context)
        c = self.get_context(vcall, request, {'form': form, 'change': False,})
        self.apply_extra_context(vcall, c, extra_context)
        self._populate_context(vcall, request)
        self.populate_context(vcall, request)
        self.get_template(vcall)
        return self.get_response(vcall)

    def dismiss_popup(self, vcall, request, obj):
        from django.utils.html import escape
        return HttpResponse('<script type="text/javascript">opener.dismissRelatedAddPopup(window, "%s", "%s");</script>' % \
                            (escape(obj._get_pk_val()), escape(obj)))

    def get_redirect(self, vcall, request, post_save_redirect = None, obj = None):
        """
        Returns a HttpResponseRedirect to ``post_save_redirect``.

        ``post_save_redirect`` should be a string, and can contain named string-
        substitution place holders of ``obj`` field names.

        If ``post_save_redirect`` is None, then redirect to ``obj``'s URL returned
        by ``get_absolute_url()``.  If ``obj`` has no ``get_absolute_url`` method,
        then raise ImproperlyConfigured.

        This function is meant to handle the post_save_redirect parameter to the
        ``create_object`` and ``update_object`` views.
        """
        assert isinstance(vcall, ViewCall)
        post_save_redirect = post_save_redirect or vcall.post_save_redirect or self.post_save_redirect
        obj                = obj or vcall.c_instance
        is_popup = string_to_bool(request.GET.get(POPUP_VARIABLE, False))
        if is_popup:
            return self.dismiss_popup(vcall, request, obj)
        if post_save_redirect:
            return HttpResponseRedirect(post_save_redirect % obj.__dict__)
        elif hasattr(obj, 'get_absolute_url'):
            return HttpResponseRedirect(obj.get_absolute_url())
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Either pass a post_save_redirect"
                " parameter to the generic view or define a get_absolute_url"
                " method on the Model.")

    def get_template(self, vcall, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        assert isinstance(vcall, ViewCall)
        model           = vcall.c_model or vcall.model
        template_name   = template_name or vcall.c_template_name or vcall.template_name or self.template_name
        template_loader = template_loader or vcall.c_template_loader or vcall.template_loader or self.template_loader
        vcall.c_template_name   = template_name
        vcall.c_template_loader = template_loader

        app_label   = model._meta.app_label
        object_name = model._meta.object_name.lower()
        template_name = template_name or ("%s/%s_create.html" % (app_label, object_name),
                                          "%s/object_create.html" % app_label,
                                          "%s_create.html" % object_name,
                                          "object_create.html",
                                          "common/object_create.html",

                                          "%s/%s_edit.html" % (app_label, object_name),
                                          "%s/object_edit.html" % app_label,
                                          "%s_edit.html" % object_name,
                                          "object_edit.html",
                                          "common/object_edit.html",

                                          "%s/%s_form.html" % (app_label, object_name),
                                          "%s/object_form.html" % app_label,
                                          "%s_form.html" % object_name,
                                          "object_form.html")
        vcall.c_template_name = template_name
        return super(CreateObjectView, self).get_template(vcall,
                                                          template_name = template_name,
                                                          template_loader = template_loader)

class UpdateObjectView(CreateObjectView):
    """
    Generic object-update view.

    Templates: ``<app_label>/<model_name>_edit.html``
               ``<app_label>/object_edit.html``
               ``<model_name>_edit.html``
               ``object_edit.html``
               ``common/object_edit.html``
               ``<app_label>/<model_name>_form.html``
               ``<app_label>/object_form.html``
               ``<model_name>_form.html``
               ``object_form.html``

    Constructor arguments:

        same as in CreateObjectView, and additionally:

        ``template_object_name``
            variable name to use in context to pass the object to the
            template.

    View call arguments:

        same as in CreateObjectView, and additionally:

        ``object_id``
            id of object to update (either this or slug+slug_field is
            required)

        ``slug``
            slug of object to update (either this or object_id is
            required)

        ``slug_field``
            field to look up slug in (defaults to ``slug``)

        ``template_object_name``

    Context:
        model:
            Model of object to be edited.
        meta:
            Meta information from the model.
        verbose_name:
            Object verbose name (model._meta.verbose_name).
        object_name:
            Object name (model._meta.object_name.lower()).
        form
            the form for the object
        object
            the original object being edited
    """

    TEMPLATE_OBJECT_NAME = 'object'

    __name__ = 'UpdateObjectView'

    def __init__(self, template_object_name = None, *args, **kwargs):
        super(UpdateObjectView, self).__init__(*args, **kwargs)
        self.template_object_name = template_object_name or self.TEMPLATE_OBJECT_NAME

    #def __call__(self, request, object_id = None, slug = None, slug_field = 'slug',
    #             model = None, form_class = None,
    #             template_name = None, template_loader = None, extra_context = {},
    #             post_save_redirect = None,
    #             login_required = None, context_processors = None,
    #             template_object_name = None,
    #             fields = None, exclude = None, fieldorder = None,
    #             formfield_callback = None, formbase = None, popup_models = None):
    def __call__(self, request, *args, **kwargs):
        """
        Update an existing object using a ModelForm.  Accepts same
        arguments as CreateObjectView, and also:

        ``object_id``
            id of object to update (either this or slug+slug_field is
            required)

        ``slug``
            slug of object to update (either this or object_id is
            required)

        ``slug_field``
            field to look up slug in (defaults to ``slug``)
        """
        vcall = self.viewcall_class(request, self, args, kwargs)
        assert isinstance(vcall, ViewCall)

        self.pre_call(vcall, request)

        model              = vcall.model or self.model
        extra_context      = vcall.extra_context or {}
        login_required     = vcall.login_required
        if login_required is None:
            login_required = self.login_required

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(vcall, request)
        if extra_context is None: extra_context = {}

        vcall.c_model = vcall.model
        self.get_model_and_form_class(vcall)
        obj = self.lookup_object(vcall)
        vcall.c_instance = obj
        form = self.get_form(vcall)

        #obj = vcall.c_form_kwargs['instance']

        if not self.check_auth(vcall, request, instance = obj, model = model):
            return self.perm_negated(vcall, request, instance = obj, model = model)

        if request.method == 'POST' and form.is_valid():
            new_object = self.save_form(vcall, form)
            if request.user.is_authenticated():
                request.user.message_set.create(message=ugettext("The %(verbose_name)s was updated successfully.") % {"verbose_name": vcall.c_model._meta.verbose_name})
            assert vcall.c_instance == new_object
            return self.get_redirect(vcall, request)

        self.apply_extra_context(vcall, extra_context, self.extra_context)
        c = self.get_context(vcall, request, {'form': form, 'change': True,})
        self.apply_extra_context(vcall, c, extra_context)
        self._populate_context(vcall, request)
        self.populate_context(vcall, request)
        self.get_template(vcall)
        response = self.get_response(vcall)
        self.populate_xheaders(vcall, request, response, vcall.c_model, getattr(obj, obj._meta.pk.attname))
        return response

    def get_form_kwargs(self, vcall, fieldorder = None, initial = None):
        assert isinstance(vcall, ViewCall)
        request = vcall.request
        form_kwargs = super(UpdateObjectView, self).get_form_kwargs(vcall, fieldorder, initial)
        form_kwargs['instance'] = vcall.c_instance
        return form_kwargs

    def lookup_object(self, vcall, model=None, object_id=None, slug=None, slug_field=None):
        """
        Return the ``model`` object with the passed ``object_id``.  If
        ``object_id`` is None, then return the the object whose ``slug_field``
        equals the passed ``slug``.  If ``slug`` and ``slug_field`` are not passed,
        then raise Http404 exception.
        """
        assert isinstance(vcall, ViewCall)
        model      = model or vcall.c_model or vcall.model or self.model
        object_id  = object_id or vcall.object_id
        slug       = slug or vcall.slug
        slug_field = slug_field or vcall.slug_field
        lookup_kwargs = {}
        if object_id:
            lookup_kwargs['%s__exact' % model._meta.pk.name] = object_id
        elif slug and slug_field:
            lookup_kwargs['%s__exact' % slug_field] = slug
        else:
            raise GenericViewError("%s view must be called with either an object_id or a slug/slug_field."
                                   % (self.__class__.__name__,))
        try:
            return model.objects.get(**lookup_kwargs)
        except ObjectDoesNotExist:
            raise Http404("No %s found for %s" % (force_unicode(model._meta.verbose_name),
                                                  lookup_kwargs))

    def dismiss_popup(self, vcall, request, obj):
        from django.utils.html import escape
        return HttpResponse('<script type="text/javascript">opener.dismissRelatedEditPopup(window, "%s", "%s");</script>' % \
                            (escape(obj._get_pk_val()), escape(obj)))

    def get_template(self, vcall, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        assert isinstance(vcall, ViewCall)
        model           = vcall.c_model or vcall.model
        template_name   = template_name or vcall.c_template_name or vcall.template_name or self.template_name
        template_loader = template_loader or vcall.c_template_loader or vcall.template_loader or self.template_loader
        vcall.c_template_name   = template_name
        vcall.c_template_loader = template_loader

        app_label   = model._meta.app_label
        object_name = model._meta.object_name.lower()
        template_name = template_name or ("%s/%s_edit.html" % (app_label, object_name),
                                          "%s/object_edit.html" % app_label,
                                          "%s_edit.html" % object_name,
                                          "object_edit.html",
                                          "common/object_edit.html",

                                          "%s/%s_form.html" % (app_label, object_name),
                                          "%s/object_form.html" % app_label,
                                          "%s_form.html" % object_name,
                                          "object_form.html")
        vcall.c_template_name = template_name
        return super(UpdateObjectView, self).get_template(vcall,
                                                          template_name = template_name,
                                                          template_loader = template_loader)

class DeleteObjectView(GenericView):
    """
    Generic object-delete function.

    The given template will be used to confirm deletetion if this view is
    fetched using GET; for safty, deletion will only be performed if this
    view is POSTed.

    Templates: ``<app_label>/<model_name>_confirm_delete.html``
               ``<app_label>/object_confirm_delete.html``
               ``<model_name>_confirm_delete.html``
               ``object_confirm_delete.html``
               ``common/object_confirm_delete.html``

    Constructor arguments:

        same as in GenericView, and additionally:

        ``post_delete_redirect``
            URL to redirect to after successful object deletion. If
            post_delete_redirect is None or an empty string, default is
            to send to the instances get_absolute_url method.

        ``template_object_name``
            variable name to use in context to pass the object to the
            template.

        ``back``
            URL to redirect to in case the confirmation dialog is cancelled.

    View call arguments:

        same as in GenericView, and additionally:

        ``model``
            Model type to delete.

        ``object_id``
            id of object to update (either this or slug+slug_field is
            required)

        ``slug``
            slug of object to update (either this or object_id is
            required)

        ``slug_field``
            field to look up slug in (defaults to ``slug``)

        ``post_delete_redirect``

        ``template_object_name``

        ``back``

    Context:
        model:
            Model of object to be deleted.
        meta:
            Meta information from the model.
        verbose_name:
            Object verbose name (model._meta.verbose_name).
        object_name:
            Object name (model._meta.object_name.lower()).
        object
            the original object being deleted
    """

    POST_DELETE_REDIRECT = None
    TEMPLATE_OBJECT_NAME = 'object'
    BACK = None

    __name__ = 'DeleteObjectView'

    def __init__(self, post_delete_redirect = None, template_object_name = None, back = None, *args, **kwargs):
        super(DeleteObjectView, self).__init__(*args, **kwargs)
        self.post_delete_redirect = post_delete_redirect or self.POST_DELETE_REDIRECT
        self.template_object_name = template_object_name or self.TEMPLATE_OBJECT_NAME
        self.back = back or self.BACK

    #def __call__(self, request, model = None, object_id = None, slug = None, slug_field = 'slug',
    #             template_name = None, template_loader = None, extra_context = {},
    #             post_delete_redirect = None,
    #             login_required = None, context_processors = None,
    #             template_object_name = None, back = None):
    def __call__(self, request, *args, **kwargs):
        vcall = self.viewcall_class(request, self, args, kwargs)
        assert isinstance(vcall, ViewCall)

        self.pre_call(vcall, request)

        model              = vcall.model or self.model
        extra_context      = vcall.extra_context or {}
        login_required     = vcall.login_required
        if login_required is None:
            login_required = self.login_required
        back               = vcall.back or self.back

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(vcall, request)
        if extra_context is None: extra_context = {}

        vcall.c_model = vcall.model
        obj = self.lookup_object(vcall)
        vcall.c_instance = obj

        if not self.check_auth(vcall, request, instance = obj, model = model):
            return self.perm_negated(vcall, request, instance = obj, model = model)

        if request.method == 'POST':
            yesno = request.POST.get('post', 'no')
            if yesno != 'yes':
                # cancel
                back = request.POST.get('back', back)
                if not back:
                    return None
                return HttpResponseRedirect(back)
            assert yesno == 'yes'

            post_delete_redirect = self.get_post_delete_redirect(vcall, request)

            self.delete_instance(vcall, obj)
            if request.user.is_authenticated():
                print "message created"
                request.user.message_set.create(message=ugettext("The %(verbose_name)s was deleted.") % {"verbose_name": model._meta.verbose_name})
            print "redirect to:%s" % repr(post_delete_redirect)
            return self.get_redirect(vcall, request, post_delete_redirect)

        assert request.method != 'POST'

        self.apply_extra_context(vcall, extra_context, self.extra_context)
        c = self.get_context(vcall, request, {})
        self.apply_extra_context(vcall, c, extra_context)
        self._populate_context(vcall, request)
        self.populate_context(vcall, request)
        self.get_template(vcall)
        response = self.get_response(vcall)
        self.populate_xheaders(vcall, request, response, vcall.c_model, getattr(obj, obj._meta.pk.attname))
        return response

    def get_template(self, vcall, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        assert isinstance(vcall, ViewCall)
        model           = vcall.c_model or vcall.model
        template_name   = template_name or vcall.c_template_name or vcall.template_name or self.template_name
        template_loader = template_loader or vcall.c_template_loader or vcall.template_loader or self.template_loader
        vcall.c_template_name   = template_name
        vcall.c_template_loader = template_loader

        app_label   = model._meta.app_label
        object_name = model._meta.object_name.lower()
        template_name = template_name or ("%s/%s_confirm_delete.html" % (app_label, object_name),
                                          "%s/object_confirm_delete.html" % app_label,
                                          "%s_confirm_delete.html" % object_name,
                                          "object_confirm_delete.html",
                                          "common/object_confirm_delete.html")
        vcall.c_template_name = template_name
        return super(DeleteObjectView, self).get_template(vcall,
                                                          template_name = template_name,
                                                          template_loader = template_loader)

    def lookup_object(self, vcall, model=None, object_id=None, slug=None, slug_field=None):
        """
        Return the ``model`` object with the passed ``object_id``.  If
        ``object_id`` is None, then return the the object whose ``slug_field``
        equals the passed ``slug``.  If ``slug`` and ``slug_field`` are not passed,
        then raise Http404 exception.
        """
        assert isinstance(vcall, ViewCall)
        model      = model or vcall.c_model or vcall.model or self.model
        object_id  = object_id or vcall.object_id
        slug       = slug or vcall.slug
        slug_field = slug_field or vcall.slug_field
        lookup_kwargs = {}
        if object_id:
            lookup_kwargs['%s__exact' % model._meta.pk.name] = object_id
        elif slug and slug_field:
            lookup_kwargs['%s__exact' % slug_field] = slug
        else:
            raise GenericViewError("%s view must be called with either an object_id or a slug/slug_field."
                                   % (self.__class__.__name__,))
        try:
            return model.objects.get(**lookup_kwargs)
        except ObjectDoesNotExist, exc:
            raise Http404("No %s found for %s" % (force_unicode(model._meta.verbose_name),
                                                  lookup_kwargs))

    def get_post_delete_redirect(self, vcall, request, post_delete_redirect=None, obj=None):
        """
        Returns a string suitable for the HttpResponseRedirect().

        ``post_delete_redirect`` should be a callable returning a string or a
        string.
        The final string can contain named string-substitution place holders of
        ``obj`` field names.
        
        Please note that this method is called BEFORE the actual object deletion,
        since ``obj`` must be valid at this time.
        """
        assert isinstance(vcall, ViewCall)
        post_delete_redirect = post_delete_redirect or vcall.post_delete_redirect or self.post_delete_redirect
        obj                  = obj or vcall.c_instance
        if post_delete_redirect and callable(post_delete_redirect):
            post_delete_redirect = post_delete_redirect(request, obj)
        if post_delete_redirect:
            post_delete_redirect = post_delete_redirect % obj.__dict__
        return post_delete_redirect

    def get_redirect(self, vcall, request, post_delete_redirect):
        """
        Returns a HttpResponseRedirect to ``post_delete_redirect``.

        ``post_delete_redirect`` should be a string, and can contain named string-
        substitution place holders of ``obj`` field names.

        If ``post_delete_redirect`` is None, we raise an ImproperlyConfigured
        exception.
        """
        assert isinstance(vcall, ViewCall)
        if post_delete_redirect:
            return HttpResponseRedirect(post_delete_redirect)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Pass a post_delete_redirect"
                " parameter to the generic view.")

class DetailObjectView(GenericView):
    """
    Generic detail of an object.

    Templates: ``<app_label>/<model_name>_detail.html``
               ``<app_label>/object_detail.html``
               ``<model_name>_detail.html``
               ``object_detail.html``

    Constructor arguments:

        same as in GenericView, and additionally:

        ``queryset``
            Queryset to retrieve object from.

        ``template_object_name``
            variable name to use in context to pass the object to the
            template.

        ``mimetype``
            mime type for the response.

        ``model``
            Model type of object to retrieve (optional, derived from queryset
            if not specified).

    View call arguments:

        same as in GenericView, and additionally:

        ``queryset``
            Queryset to retrieve object from.

        ``object_id``
            id of object to update (either this or slug+slug_field is
            required)

        ``slug``
            slug of object to update (either this or object_id is
            required)

        ``slug_field``
            field to look up slug in (defaults to ``slug``)

        ``mimetype``
            mime type for the response.

        ``model``
            Model type of object to retrieve (optional, derived from queryset
            if not specified).

        ``template_object_name``

    Context:
        model:
            Model of object to be displayed.
        meta:
            Meta information from the model.
        verbose_name:
            Object verbose name (model._meta.verbose_name).
        object_name:
            Object name (model._meta.object_name.lower()).
        object
            the object
    """

    QUERYSET = None
    TEMPLATE_OBJECT_NAME = 'object'
    MIMETYPE = None
    MODEL = None

    __name__ = 'DetailObjectView'

    def __init__(self, queryset = None, template_object_name = None, mimetype = None, model = None, *args, **kwargs):
        super(DetailObjectView, self).__init__(*args, **kwargs)
        if queryset is not None:
            self.queryset = queryset
        else:
            self.queryset = self.QUERYSET
        self.model    = model or self.MODEL
        self.mimetype = mimetype or self.MIMETYPE
        self.template_object_name = template_object_name or self.TEMPLATE_OBJECT_NAME

    #def __call__(self, request, queryset = None, object_id = None, slug = None, slug_field = 'slug',
    #             template_name = None, template_loader = None, extra_context = {},
    #             login_required = None, context_processors = None,
    #             template_object_name = None, mimetype = None, model = None):
    def __call__(self, request, *args, **kwargs):
        """
        Generic object detail view function.
        """
        vcall = self.viewcall_class(request, self, args, kwargs)
        assert isinstance(vcall, ViewCall)

        self.pre_call(vcall, request)

        queryset = vcall.queryset
        if queryset is None:
            queryset = self.queryset
        object_id          = vcall.object_id
        slug               = vcall.slug
        slug_field         = vcall.slug_field
        model              = vcall.model or self.model or queryset.model
        extra_context      = vcall.extra_context or {}
        login_required     = vcall.login_required
        if login_required is None:
            login_required = self.login_required

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(vcall, request)
        if extra_context is None: extra_context = {}

        model = model or queryset.model
        vcall.c_model = model
        vcall.c_queryset = queryset

        obj = self.lookup_object(vcall)
        vcall.c_instance = obj

        if not self.check_auth(vcall, request, queryset = queryset, instance = obj, model = model):
            return self.perm_negated(vcall, request, queryset = queryset, instance = obj, model = model)

        self.apply_extra_context(vcall, extra_context, self.extra_context)
        c = self.get_context(vcall, request, {})
        self.apply_extra_context(vcall, c, extra_context)
        self._populate_context(vcall, request)
        self.populate_context(vcall, request)
        self.get_template(vcall)
        response = self.get_response(vcall)
        self.populate_xheaders(vcall, request, response, model, getattr(obj, obj._meta.pk.attname))
        return response

    def get_template(self, vcall, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        assert isinstance(vcall, ViewCall)
        model           = vcall.c_model or vcall.model
        template_name   = template_name or vcall.c_template_name or vcall.template_name or self.template_name
        template_loader = template_loader or vcall.c_template_loader or vcall.template_loader or self.template_loader
        vcall.c_template_name   = template_name
        vcall.c_template_loader = template_loader

        app_label   = model._meta.app_label
        object_name = model._meta.object_name.lower()
        template_name = template_name or ("%s/%s_detail.html" % (app_label, object_name),
                                          "%s/object_detail.html" % app_label,
                                          "%s_detail.html" % object_name,
                                          "object_detail.html",
                                          "common/object_detail.html")
        vcall.c_template_name = template_name
        return super(DetailObjectView, self).get_template(vcall,
                                                          template_name = template_name,
                                                          template_loader = template_loader)

    def lookup_object(self, vcall, queryset=None, model=None, object_id=None, slug=None, slug_field=None):
        """
        Return the ``model`` object with the passed ``object_id``.  If
        ``object_id`` is None, then return the the object whose ``slug_field``
        equals the passed ``slug``.  If ``slug`` and ``slug_field`` are not passed,
        then raise Http404 exception.
        """
        assert isinstance(vcall, ViewCall)
        queryset   = queryset
        if queryset is None:
            queryset = vcall.c_queryset
        if queryset is None:
            queryset = vcall.queryset
        if queryset is None:
            queryset = self.queryset
        model      = model or vcall.c_model or vcall.model or self.model
        if (model is None) and (queryset is not None):
            model = queryset.model
        object_id  = object_id or vcall.object_id
        slug       = slug or vcall.slug
        slug_field = slug_field or vcall.slug_field

        obj = None
        if queryset:
            if object_id:
                queryset = queryset.filter(pk = object_id)
            elif slug and slug_field:
                queryset = queryset.filter(**{slug_field: slug})
            else:
                raise GenericViewError("%s view must be called with either an object_id or a slug/slug_field."
                                       % (self.__class__.__name__,))
            try:
                obj = queryset.get()
            except ObjectDoesNotExist, exc:
                raise Http404("No %s found matching the query" % (force_unicode(model._meta.verbose_name),))
            return obj

        lookup_kwargs = {}
        if object_id:
            lookup_kwargs['%s__exact' % model._meta.pk.name] = object_id
        elif slug and slug_field:
            lookup_kwargs['%s__exact' % slug_field] = slug
        else:
            raise GenericViewError("%s view must be called with either an object_id or a slug/slug_field."
                                   % (self.__class__.__name__,))
        try:
            return model.objects.get(**lookup_kwargs)
        except ObjectDoesNotExist, exc:
            raise Http404("No %s found for %s" % (force_unicode(model._meta.verbose_name),
                                                  lookup_kwargs))
        return obj

class ListObjectView(GenericView):
    """
    Generic list of objects.

    Templates: ``<app_label>/<model_name>_list.html``
               ``<app_label>/object_list.html``
               ``<model_name>_list.html``
               ``object_list.html``

    Constructor arguments:

        same as in GenericView, and additionally:

        ``queryset``
            Queryset to retrieve objects from.

        ``paginate_by``
            Number of objects per page.

        ``allow_empty``
            If False raise an exception on empty queryset (default: True).

        ``template_object_name``
            variable name to use in context to pass the object to the
            template.

        ``mimetype``
            mime type for the response.

        ``model``
            Model type of objects to retrieve (optional, derived from queryset
            if not specified).

    View call arguments:

        same as in GenericView, and additionally:

        ``queryset``

        ``paginate_by``

        ``page``
            page number to display

        ``allow_empty``

        ``mimetype``

        ``model``

        ``template_object_name``

    Context:
        model:
            Model of objects in the object_list.
        meta:
            Meta information from the model.
        verbose_name:
            Object verbose name (model._meta.verbose_name).
        object_name:
            Object name (model._meta.object_name.lower()).
        object_list
            list of objects
        is_paginated
            are the results paginated?
        results_per_page
            number of objects per page (if paginated)
        has_next
            is there a next page?
        has_previous
            is there a prev page?
        page
            the current page
        next
            the next page
        previous
            the previous page
        pages
            number of pages, total
        hits
            number of objects, total
        last_on_page
            the result number of the last of object in the
            object_list (1-indexed)
        first_on_page
            the result number of the first object in the
            object_list (1-indexed)
        page_range:
            A list of the page numbers (1-indexed).
    """

    QUERYSET = None
    PAGINATE_BY = None
    ALLOW_EMPTY = True
    TEMPLATE_OBJECT_NAME = 'object'
    MIMETYPE = None
    MODEL = None
    LOOKUP_KWARGS = None

    __name__ = 'ListObjectView'

    def __init__(self, queryset = None,
                 paginate_by = None, allow_empty = None,
                 template_object_name = None, mimetype = None, model = None,
                 lookup_kwargs = None,
                 *args, **kwargs):
        super(ListObjectView, self).__init__(*args, **kwargs)
        if queryset is not None:
            self.queryset = queryset
        else:
            self.queryset = self.QUERYSET
        self.model       = model or self.MODEL
        self.paginate_by = paginate_by or self.PAGINATE_BY
        if allow_empty is not None:
            self.allow_empty = allow_empty
        else:
            self.allow_empty = self.ALLOW_EMPTY
        self.mimetype    = mimetype or self.MIMETYPE
        self.template_object_name = template_object_name or self.TEMPLATE_OBJECT_NAME
        self.lookup_kwargs = lookup_kwargs or self.LOOKUP_KWARGS

    def get_paginator(self, vcall, request, queryset = None, paginate_by = None, allow_empty = None, page = None):
        assert isinstance(vcall, ViewCall)
        if queryset is None:
            queryset = vcall.c_queryset
        if queryset is None:
            queryset = vcall.queryset
        if queryset is None:
            queryset = self.queryset
        paginate_by = paginate_by or vcall.paginate_by or self.paginate_by
        allow_empty  = vcall.allow_empty
        if allow_empty is None:
            allow_empty = self.allow_empty
        return Paginator(queryset, paginate_by, allow_empty_first_page=allow_empty)

    def get_page(self, vcall, request, page, pagename = 'page'):
        if not page:
            page = request.GET.get(pagename, 1)
        return page

    #def __call__(self, request, queryset = None,
    #             paginate_by = None, page = None, allow_empty = None,
    #             template_name = None, template_loader = None, extra_context = {},
    #             login_required = None, context_processors = None,
    #             template_object_name = None, mimetype = None, model = None,
    #             lookup_kwargs = None, **kwargs):
    def __call__(self, request, *args, **kwargs):
        """
        Generic object list view function.
        """
        vcall = self.viewcall_class(request, self, args, kwargs)
        assert isinstance(vcall, ViewCall)

        self.pre_call(vcall, request)

        queryset = vcall.queryset
        if queryset is None:
            queryset = self.queryset
        paginate_by        = vcall.paginate_by or self.paginate_by
        allow_empty        = vcall.allow_empty
        if allow_empty is None:
            allow_empty = self.allow_empty
        page               = vcall.page
        extra_context      = vcall.extra_context or {}
        login_required     = vcall.login_required
        if login_required is None:
            login_required = self.login_required
        model              = vcall.model or self.model
        lookup_kwargs      = vcall.lookup_kwargs or self.lookup_kwargs

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(vcall, request)
        if extra_context is None: extra_context = {}

        queryset = queryset._clone()
        model    = model or queryset.model
        vcall.c_model = model
        vcall.c_queryset = queryset

        if lookup_kwargs is not None:
            filter_kwargs = {}
            for k, v in lookup_kwargs.items():
                if k in kwargs:
                    filter_kwargs[k] = kwargs[k]
            queryset = queryset.filter(**filter_kwargs)
        vcall.c_queryset = queryset

        if not self.check_auth(vcall, request, queryset = queryset, model = model):
            return self.perm_negated(vcall, request, queryset = queryset, model = model)

        # TODO: handle filtered querysets (we need to special-case pagination too)
        # queryset = self.filter_queryset(request, queryset = queryset, model = model)

        if paginate_by:
            paginator = self.get_paginator(vcall, request)
            vcall.c_paginator = paginator
            page = self.get_page(vcall, request, page)
            vcall.c_page = page
            try:
                page_number = int(page)
                vcall.c_page_num = page_number
            except ValueError:
                if page == 'last':
                    page_number = paginator.num_pages
                    vcall.c_page_num = page_number
                else:
                    # Page is not 'last', nor can it be converted to an int.
                    raise Http404
            try:
                page_obj = paginator.page(page_number)
                vcall.c_page_obj = page_obj
            except InvalidPage:
                raise Http404

            vcall.c_object_list  = page_obj.object_list
            vcall.c_is_paginated = True

            c = self.get_context(vcall, request, {
                '%s_list' % vcall.template_object_name: page_obj.object_list,
                'paginator': paginator,
                'page_obj': page_obj,

                # Legacy template context stuff. New templates should use page_obj
                # to access this instead.
                'is_paginated': page_obj.has_other_pages(),
                'results_per_page': paginator.per_page,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'page': page_obj.number,
                'next': page_obj.next_page_number(),
                'previous': page_obj.previous_page_number(),
                'first_on_page': page_obj.start_index(),
                'last_on_page': page_obj.end_index(),
                'pages': paginator.num_pages,
                'hits': paginator.count,
                'page_range': paginator.page_range,
                })
        else:
            vcall.c_object_list  = queryset
            vcall.c_is_paginated = False
            c = self.get_context(vcall, request, {
                '%s_list' % vcall.template_object_name: queryset,
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                })
            if not allow_empty and len(queryset) == 0:
                raise Http404
        self.apply_extra_context(vcall, extra_context, self.extra_context)
        self.apply_extra_context(vcall, c, extra_context)
        self._populate_context(vcall, request)
        self.populate_context(vcall, request)
        self.get_template(vcall)
        response = self.get_response(vcall)
        return response

    def get_template(self, vcall, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        assert isinstance(vcall, ViewCall)
        model           = vcall.c_model or vcall.model
        template_name   = template_name or vcall.c_template_name or vcall.template_name or self.template_name
        template_loader = template_loader or vcall.c_template_loader or vcall.template_loader or self.template_loader
        vcall.c_template_name   = template_name
        vcall.c_template_loader = template_loader

        app_label   = model._meta.app_label
        object_name = model._meta.object_name.lower()
        template_name = template_name or ("%s/%s_list.html" % (app_label, object_name),
                                          "%s/object_list.html" % app_label,
                                          "%s_list.html" % object_name,
                                          "object_list.html",
                                          "common/object_list.html")
        vcall.c_template_name = template_name
        return super(ListObjectView, self).get_template(vcall,
                                                          template_name = template_name,
                                                          template_loader = template_loader)

# ------------------------------------------------------------------------
#   FUNCTIONAL GENERIC VIEWS
# ------------------------------------------------------------------------

create_object = CreateObjectView()
update_object = UpdateObjectView()
delete_object = DeleteObjectView()
object_detail = DetailObjectView()
object_list   = ListObjectView()
