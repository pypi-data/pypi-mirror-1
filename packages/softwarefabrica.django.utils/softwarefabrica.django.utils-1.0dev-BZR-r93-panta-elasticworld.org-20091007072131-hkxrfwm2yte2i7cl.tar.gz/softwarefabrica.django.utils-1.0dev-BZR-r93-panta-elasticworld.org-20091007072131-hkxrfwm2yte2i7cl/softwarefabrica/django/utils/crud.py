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

from django.forms.models import ModelFormMetaclass, ModelForm, BaseModelForm
from django.template import RequestContext, loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.xheaders import populate_xheaders
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.utils.translation import ugettext
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator, InvalidPage
from django.views.generic import GenericViewError

from django.utils.encoding import force_unicode, smart_str
from django import forms
from django.forms.forms import BoundField

#
# HACK TODO: for some reason, I need to use "ModelForm" as a base for
#            BaseModelFormFieldOrder, instead of "BaseModelForm", as
#            it would seem more natural to me.
#
#class BaseModelFormFieldOrder(BaseModelForm):
#    def __init__(self, fieldorder = None, *args, **kwargs):
#        super(BaseModelFormFieldOrder, self).__init__(*args, **kwargs)
#        if fieldorder:
#            self.fields.keyOrder = list(fieldorder)

class BaseModelFormFieldOrder(ModelForm):
    def __init__(self, fieldorder = None, *args, **kwargs):
        super(BaseModelFormFieldOrder, self).__init__(*args, **kwargs)
        if fieldorder:
            self.fields.keyOrder = list(fieldorder)

class ModelFormFieldOrder(BaseModelFormFieldOrder):
    __metaclass__ = ModelFormMetaclass

# Form class outputting via template
#
# see:
#   http://code.djangoproject.com/wiki/TemplatedForm
class TemplatedForm(forms.Form):
    def __init__(self, template_name = 'forms/form.html', template_loader = loader, *args, **kwargs):
        """
        Template-based form

        Constructor arguments:

        ``template_name``
            name of template to use, or list of templates.

        ``template_loader``
            template loader to use (defaults to django.template.loader).
        """

        super(TemplatedForm, self).__init__(*args, **kwargs)
        self.template_name   = template_name
        self.template_loader = template_loader

    def get_template(self, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        template_name   = template_name or self.template_name
        template_loader = template_loader or self.template_loader
        if isinstance(template_name, (list, tuple)):
            return template_loader.select_template(template_name)
        else:
            return template_loader.get_template(template_name)

    def get_response(self, template, context_instance, mimetype = None):
        """
        Return a HttpResponse object based on given request, template,
        and context.
        """
        if mimetype is not None:
            return HttpResponse(template.render(context_instance), mimetype = mimetype)
        return HttpResponse(template.render(context_instance))

    def output_via_template(self, template_name = None, template_loader = None):
        "Helper function for rendering form via template."
        bound_fields = [BoundField(self, field, name) for name, field \
                        in self.fields.items()]
        c = Context(dict(form = self, bound_fields = bound_fields))
        t = self.get_template(template_name, template_loader)
        return self.get_response(t, c)

    def __unicode__(self):
        return self.output_via_template()

# ------------------------------------------------------------------------
#   OBJECT-ORIENTED GENERIC VIEWS
# ------------------------------------------------------------------------

class View(object):
    """
    Object-oriented base view.
    """ 

    def __init__(self, template_name = None, template_loader = loader, extra_context = {}, login_required = False, context_processors = None):
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

        self.template_name      = template_name
        self.template_loader    = template_loader
        self.extra_context      = extra_context or {}
        self.login_required     = login_required
        self.context_processors = context_processors

    def __call__(self, request,
                 template_name = None, template_loader = None,
                 extra_context = {}, login_required = None,
                 context_processors = None):
        """
        Arguments:

        ``request``
            The HttpRequest object.
        """

        template_name      = template_name or self.template_name
        template_loader    = template_loader or self.template_loader
        extra_context      = extra_context or {}
        login_required     = login_required or self.login_required
        context_processors = context_processors or self.context_processors

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(request)
        if extra_context is None: extra_context = {}
        extra_context = self.apply_extra_context(extra_context, self.extra_context)
        c = self.get_context(request, {}, context_processors)
        c = self.apply_extra_context(c, extra_context)
        c = self.append_to_context(c, request)
        t = self.get_template(template_name, template_loader)
        return self.get_response(t, c)

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

    def apply_extra_context(self, context, extra_context = None):
        extra_context = extra_context or self.extra_context
        return self.merge_dict(context, extra_context)

    def append_to_context(self, context, request):
        """
        Override to add additional contents to the context.
        """
        return self

    def get_template(self, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        template_name   = template_name or self.template_name
        template_loader = template_loader or self.template_loader
        if isinstance(template_name, (list, tuple)):
            return template_loader.select_template(template_name)
        else:
            return template_loader.get_template(template_name)

    def get_context(self, request, dictionary = {}, context_processors = None):
        """
        Return a context instance with data in ``dictionary``.
        """
        context_processors = context_processors or self.context_processors
        return RequestContext(request, dictionary, context_processors)

    def get_response(self, template, context_instance, mimetype = None):
        """
        Return a HttpResponse object based on given request, template,
        and context.
        """
        if mimetype is not None:
            return HttpResponse(template.render(context_instance), mimetype = mimetype)
        return HttpResponse(template.render(context_instance))

    def populate_xheaders(self, request, response, model, object_id):
        populate_xheaders(request, response, model, object_id)
        return response

    def redirect_to_login(self, request):
        return redirect_to_login(request.path)

class GenericView(View):
    def __init__(self, model = None, form_class = None,
                 template_name = None, template_loader = loader,
                 extra_context = None, login_required = False, context_processors = None,
                 fields = None, exclude = None, fieldorder = None, formfield_callback = None, formbase = ModelFormFieldOrder):
        """
        Arguments:

        ``model``
            Model type to create (either this or form_class is required)

        ``form_class``
            ModelForm subclass to use (either this or model is required)
        """

        super(GenericView, self).__init__(template_name, template_loader, extra_context, login_required, context_processors)
        self.fields             = fields
        self.exclude            = exclude
        self.fieldorder         = fieldorder
        self.formfield_callback = formfield_callback
        self.formbase           = formbase

        self.model              = model
        self.form_class         = form_class

        # cached by get_model_and_form_class()
        self.c_model            = None
        self.c_form_class       = None

    def __call__(self, request, model = None, form_class = None,
                 template_name = None, template_loader = None,
                 extra_context = {},
                 login_required = None, context_processors = None,
                 fields = None, exclude = None, fieldorder = None,
                 formfield_callback = None, formbase = None):

        model              = model or self.model
        form_class         = form_class or self.form_class
        template_name      = template_name or self.template_name
        template_loader    = template_loader or self.template_loader
        extra_context      = extra_context or {}
        login_required     = login_required or self.login_required
        context_processors = context_processors or self.context_processors
        fields             = fields or self.fields
        exclude            = exclude or self.exclude
        fieldorder         = fieldorder or self.fieldorder
        formfield_callback = formfield_callback or self.formfield_callback
        formbase           = formbase or self.formbase

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(request)
        if extra_context is None: extra_context = {}

        (self.c_model, self.c_form_class) = self.get_model_and_form_class(model, form_class,
                                                                          fields, exclude, formfield_callback, formbase)
        (form, form_kwargs) = self.get_form(request, self.c_form_class, fieldorder)

        extra_context = self.apply_extra_context(extra_context, self.extra_context)
        c = self.get_context(request, {'form': form}, context_processors)
        c = self.apply_extra_context(c, extra_context)
        c = self.append_to_context(c, request, self.c_model)
        t = self.get_template(self.c_model, template_name, template_loader)
        return self.get_response(t, c)

    def append_to_context(self, context, request, model, obj = None, template_object_name = 'object'):
        super(GenericView, self).append_to_context(context, request)
        opts         = model._meta
        verbose_name = force_unicode(opts.verbose_name)
        object_name  = force_unicode(opts.object_name.lower())
        context['model']        = model
        context['meta']         = opts
        context['verbose_name'] = verbose_name
        context['object_name']  = object_name
        if obj is not None:
            context[template_object_name] = obj
            context[template_object_name + '_id'] = getattr(obj, obj._meta.pk.attname)
        return context

    def get_template(self, model = None, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        model           = model or self.c_model
        template_name   = template_name or self.template_name
        template_loader = template_loader or self.template_loader

        app_label   = model._meta.app_label
        object_name = model._meta.object_name.lower()
        template_name = template_name or ("%s/%s_form.html" % (app_label, object_name),
                                          "%s/object_form.html" % app_label,
                                          "%s_form.html" % object_name,
                                          "object_form.html")
        return super(GenericView, self).get_template(template_name, template_loader)

    def get_model_and_form_class(self, _model = None, form_class = None,
                                 _fields = None, _exclude = None,
                                 formfield_callback = lambda f: f.formfield(),
                                 form = ModelFormFieldOrder):
        """
        Returns a model and form class based on the model and form_class
        parameters that were passed to the generic view.

        If ``form_class`` is given then its associated model will be returned along
        with ``form_class`` itself.  Otherwise, if ``model`` is given, ``model``
        itself will be returned along with a ``ModelForm`` class created from
        ``model``.

        ``form`` is the form base class used (passed to ModelFormMetaclass to create
        the final form class).
        """
        _model     = _model or self.model
        form_class = form_class or self.form_class
        #
        # inspired by modelform_factory()
        # see django_src/django/forms/models.py
        #
        # for dynamic ModelForm see:
        #   http://blog.handimobility.ca/tag/django/
        #   http://whynoti.org/blog/django/forms/models.py
        if form_class:
            return form_class._meta.model, form_class
        if _model:
            #if formfield_callback is not None:
            #    form_class = modelform_factory(_model, form = ModelForm,
            #                                   fields = _fields, exclude = _exclude,
            #                                   formfield_callback = formfield_callback)
            #    return _model, form_class

            # The inner Meta class fails if model = model is used for some reason.
            tmp_model = _model
            # HACK TODO: we should be able to construct a ModelForm without creating
            # and passing in a temporary inner class.
            class Meta:
                pass
            setattr(Meta, 'model', _model)
            if _fields is not None:
                setattr(Meta, 'fields', _fields)
            if _exclude is not None:
                setattr(Meta, 'exclude', _exclude)
            class_name = _model.__name__ + 'Form'
            attrs = {'Meta': Meta}
            if formfield_callback is not None:
                attrs['formfield_callback'] = formfield_callback
            form_class = ModelFormMetaclass(class_name, (form,), attrs)
            # for field ordering, see:
            #   http://code.djangoproject.com/wiki/CookBookNewFormsFieldOrdering
            return _model, form_class
        raise GenericViewError("%s view must be called with either a model or"
                               " form_class argument." % (self.__class__.__name__,))

    def get_form_kwargs(self, request):
        """
        Get dictionary of arguments to construct the appropriate
        ``form_class`` instance.
        """
        if request.method == 'POST':
            return {'data': request.POST, 'files': request.FILES}
        return {}

    def get_form(self, request, form_class = None, fieldorder = None, initial = None):
        """
        Return the appropriate ``form_class`` instance based on the
        ``request``.
        """
        form_class = form_class or self.c_form_class
        fieldorder = fieldorder or self.fieldorder
        form_kwargs = self.get_form_kwargs(request)
        if fieldorder:
            form_kwargs['fieldorder'] = fieldorder
        if initial:
            form_kwargs['initial'] = initial
        print "form kwargs:%s" % repr(form_kwargs)
        return (form_class(**form_kwargs), form_kwargs)

    def save_instance(self, obj, form=None):
        """
        Save and return model instance.
        """
        obj.save()
        if form:
            self.save_m2m(form)
        return obj

    def save_m2m(self, form):
        """
        Save the many-to-many related data.
        """
        form.save_m2m()
        return self

    def delete_instance(self, obj):
        """
        Delete the given model instance.
        """
        obj.delete()
        return self

    def save_form(self, form):
        """
        Save form, returning saved object.
        """
        return self.save_instance(form.save(commit=False), form)


class CreateObjectView(GenericView):
    """
    Generic object-creation view.

    Templates: ``<app_label>/<model_name>_form.html``
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

    def __init__(self, post_save_redirect = None, *args, **kwargs):
        super(CreateObjectView, self).__init__(*args, **kwargs)
        self.post_save_redirect = post_save_redirect

    def __call__(self, request, model = None, form_class = None,
                 template_name = None, template_loader = None, extra_context = {},
                 post_save_redirect = None,
                 login_required = None, context_processors = None,
                 fields = None, exclude = None, fieldorder = None,
                 formfield_callback = None, formbase = None, form_initial = None):

        model              = model or self.model
        form_class         = form_class or self.form_class
        template_name      = template_name or self.template_name
        template_loader    = template_loader or self.template_loader
        extra_context      = extra_context or {}
        post_save_redirect = post_save_redirect or self.post_save_redirect
        login_required     = login_required or self.login_required
        context_processors = context_processors or self.context_processors
        fields             = fields or self.fields
        exclude            = exclude or self.exclude
        fieldorder         = fieldorder or self.fieldorder
        formfield_callback = formfield_callback or self.formfield_callback
        formbase           = formbase or self.formbase

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(request)
        if extra_context is None: extra_context = {}

        (self.c_model, self.c_form_class) = self.get_model_and_form_class(model, form_class,
                                                                          fields, exclude, formfield_callback, formbase)
        (form, form_kwargs) = self.get_form(request, self.c_form_class, fieldorder, initial = form_initial)

        if request.method == 'POST' and form.is_valid():
            new_object = self.save_form(form)
            if request.user.is_authenticated():
                request.user.message_set.create(message=ugettext("The %(verbose_name)s was created successfully.") % {"verbose_name": self.c_model._meta.verbose_name})
            return self.get_redirect(request, post_save_redirect, new_object)

        extra_context = self.apply_extra_context(extra_context, self.extra_context)
        c = self.get_context(request, {'form': form, 'change': False,}, context_processors)
        c = self.apply_extra_context(c, extra_context)
        c = self.append_to_context(c, request, self.c_model)
        t = self.get_template(self.c_model, template_name, template_loader)
        return self.get_response(t, c)

    def get_redirect(self, request, post_save_redirect, obj):
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
        if post_save_redirect:
            return HttpResponseRedirect(post_save_redirect % obj.__dict__)
        elif hasattr(obj, 'get_absolute_url'):
            return HttpResponseRedirect(obj.get_absolute_url())
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Either pass a post_save_redirect"
                " parameter to the generic view or define a get_absolute_url"
                " method on the Model.")

class UpdateObjectView(CreateObjectView):
    """
    Generic object-update view.

    Templates: ``<app_label>/<model_name>_form.html``
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

    def __init__(self, template_object_name = 'object', *args, **kwargs):
        super(UpdateObjectView, self).__init__(*args, **kwargs)
        self.template_object_name = template_object_name

    def __call__(self, request, object_id = None, slug = None, slug_field = 'slug',
                 model = None, form_class = None,
                 template_name = None, template_loader = None, extra_context = {},
                 post_save_redirect = None,
                 login_required = None, context_processors = None,
                 template_object_name = None,
                 fields = None, exclude = None, fieldorder = None,
                 formfield_callback = None, formbase = None):
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

        model              = model or self.model
        form_class         = form_class or self.form_class
        template_name      = template_name or self.template_name
        template_loader    = template_loader or self.template_loader
        extra_context      = extra_context or {}
        post_save_redirect = post_save_redirect or self.post_save_redirect
        login_required     = login_required or self.login_required
        context_processors = context_processors or self.context_processors
        template_object_name = template_object_name or self.template_object_name
        fields             = fields or self.fields
        exclude            = exclude or self.exclude
        fieldorder         = fieldorder or self.fieldorder
        formfield_callback = formfield_callback or self.formfield_callback
        formbase           = formbase or self.formbase

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(request)
        if extra_context is None: extra_context = {}

        self.object_id  = object_id
        self.slug       = slug
        self.slug_field = slug_field

        (self.c_model, self.c_form_class) = self.get_model_and_form_class(model, form_class,
                                                                          fields, exclude, formfield_callback, formbase)
        (form, form_kwargs) = self.get_form(request, self.c_form_class, fieldorder)
        obj = form_kwargs['instance']

        if request.method == 'POST' and form.is_valid():
            new_object = self.save_form(form)
            if request.user.is_authenticated():
                request.user.message_set.create(message=ugettext("The %(verbose_name)s was updated successfully.") % {"verbose_name": self.c_model._meta.verbose_name})
            return self.get_redirect(request, post_save_redirect, new_object)

        extra_context = self.apply_extra_context(extra_context, self.extra_context)
        c = self.get_context(request, {'form': form, 'change': True,}, context_processors)
        c = self.apply_extra_context(c, extra_context)
        c = self.append_to_context(c, request, self.c_model, obj, template_object_name)
        t = self.get_template(self.c_model, template_name, template_loader)
        response = self.get_response(t, c)
        self.populate_xheaders(request, response, self.c_model, getattr(obj, obj._meta.pk.attname))
        return response

    def get_form_kwargs(self, request):
        instance = self.lookup_object(self.c_model, self.object_id,
                                      self.slug, self.slug_field)
        kwargs = super(UpdateObjectView, self).get_form_kwargs(request)
        kwargs['instance'] = instance
        return kwargs

    def lookup_object(self, model, object_id, slug, slug_field):
        """
        Return the ``model`` object with the passed ``object_id``.  If
        ``object_id`` is None, then return the the object whose ``slug_field``
        equals the passed ``slug``.  If ``slug`` and ``slug_field`` are not passed,
        then raise Http404 exception.
        """
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
            raise Http404("No %s found for %s" % (model._meta.verbose_name,
                                                  lookup_kwargs))

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

    def __init__(self, post_delete_redirect = None, template_object_name = 'object', back = None, *args, **kwargs):
        super(DeleteObjectView, self).__init__(*args, **kwargs)
        self.post_delete_redirect = post_delete_redirect
        self.template_object_name = template_object_name
        self.back = back

    def __call__(self, request, model = None, object_id = None, slug = None, slug_field = 'slug',
                 template_name = None, template_loader = None, extra_context = {},
                 post_delete_redirect = None,
                 login_required = None, context_processors = None,
                 template_object_name = None, back = None):

        model              = model or self.model
        form_class         = form_class or self.form_class
        template_name      = template_name or self.template_name
        template_loader    = template_loader or self.template_loader
        extra_context      = extra_context or {}
        post_delete_redirect = post_delete_redirect or self.post_delete_redirect
        login_required     = login_required or self.login_required
        context_processors = context_processors or self.context_processors
        template_object_name = template_object_name or self.template_object_name
        back               = back or self.back

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(request)
        if extra_context is None: extra_context = {}

        obj = self.lookup_object(model, object_id, slug, slug_field)

        if request.method == 'POST':
            yesno = request.POST.get('post', 'no')
            if yesno != 'yes':
                # cancel
                back = request.POST.get('back', back)
                if not back:
                    return None
                return HttpResponseRedirect(back)
            assert yesno == 'yes'

            self.delete_instance(obj)
            if request.user.is_authenticated():
                request.user.message_set.create(message=ugettext("The %(verbose_name)s was deleted.") % {"verbose_name": model._meta.verbose_name})
            return HttpResponseRedirect(post_delete_redirect)

        assert request.method != 'POST'

        extra_context = self.apply_extra_context(extra_context, self.extra_context)
        c = self.get_context(request, {}, context_processors)
        c = self.apply_extra_context(c, extra_context)
        c = self.append_to_context(c, request, model, obj, template_object_name)
        t = self.get_template(model, template_name, template_loader)
        response = self.get_response(t, c)
        self.populate_xheaders(request, response, model, getattr(obj, obj._meta.pk.attname))
        return response

    def get_template(self, model, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        template_name   = template_name or self.template_name
        template_loader = template_loader or self.template_loader
        app_label   = model._meta.app_label
        object_name = model._meta.object_name.lower()
        template_name = template_name or ("%s/%s_confirm_delete.html" % (app_label, object_name),
                                          "%s/object_confirm_delete.html" % app_label,
                                          "%s_confirm_delete.html" % object_name,
                                          "object_confirm_delete.html")
        return super(DeleteObjectView, self).get_template(model, template_name, template_loader)

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

    def __init__(self, queryset = None, template_object_name = 'object', mimetype = None, model = None, *args, **kwargs):
        super(DetailObjectView, self).__init__(*args, **kwargs)
        self.queryset = queryset
        self.model    = model
        self.mimetype = mimetype
        self.template_object_name = template_object_name

    def __call__(self, request, queryset = None, object_id = None, slug = None, slug_field = 'slug',
                 template_name = None, template_loader = None, extra_context = {},
                 login_required = None, context_processors = None,
                 template_object_name = None, mimetype = None, model = None):
        """
        Generic object detail view function.
        """

        if queryset is None: queryset = self.queryset
        template_name      = template_name or self.template_name
        template_loader    = template_loader or self.template_loader
        extra_context      = extra_context or {}
        login_required     = login_required or self.login_required
        context_processors = context_processors or self.context_processors
        template_object_name = template_object_name or self.template_object_name
        mimetype           = mimetype or self.mimetype
        model              = model or self.model

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(request)
        if extra_context is None: extra_context = {}

        model = model or queryset.model
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
            except ObjectDoesNotExist:
                raise Http404("No %s found matching the query" % (model._meta.verbose_name,))
        else:
            obj = self.lookup_object(model, object_id, slug, slug_field)

        extra_context = self.apply_extra_context(extra_context, self.extra_context)
        c = self.get_context(request, {}, context_processors)
        c = self.apply_extra_context(c, extra_context)
        c = self.append_to_context(c, request, model, obj, template_object_name)
        t = self.get_template(model, template_name, template_loader)
        response = self.get_response(t, c, mimetype)
        self.populate_xheaders(request, response, model, getattr(obj, obj._meta.pk.attname))
        return response

    def get_template(self, model, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        template_name   = template_name or self.template_name
        template_loader = template_loader or self.template_loader
        app_label   = model._meta.app_label
        object_name = model._meta.object_name.lower()
        template_name = template_name or ("%s/%s_detail.html" % (app_label, object_name),
                                          "%s/object_detail.html" % app_label,
                                          "%s_detail.html" % object_name,
                                          "object_detail.html")
        return super(DetailObjectView, self).get_template(model, template_name, template_loader)

    def lookup_object(self, model, object_id, slug, slug_field):
        """
        Return the ``model`` object with the passed ``object_id``.  If
        ``object_id`` is None, then return the the object whose ``slug_field``
        equals the passed ``slug``.  If ``slug`` and ``slug_field`` are not passed,
        then raise Http404 exception.
        """
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
            raise Http404("No %s found for %s" % (model._meta.verbose_name,
                                                  lookup_kwargs))

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

    def __init__(self, queryset = None,
                 paginate_by = None, allow_empty = True,
                 template_object_name = 'object', mimetype = None, model = None,
                 lookup_kwargs = None,
                 *args, **kwargs):
        super(ListObjectView, self).__init__(*args, **kwargs)
        self.queryset    = queryset
        self.model       = model
        self.paginate_by = paginate_by
        self.allow_empty = allow_empty
        self.mimetype    = mimetype
        self.template_object_name = template_object_name
        self.lookup_kwargs = lookup_kwargs

    def paginator(self, request, queryset = None, paginate_by = None, allow_empty = None, page = None):
        if queryset is None: queryset = self.queryset
        paginate_by = paginate_by or self.paginate_by
        allow_empty = allow_empty or self.allow_empty
        return Paginator(queryset, paginate_by, allow_empty_first_page=allow_empty)

    def page(self, request, page, pagename = 'page'):
        if not page:
            page = request.GET.get(pagename, 1)
        return page

    def __call__(self, request, queryset = None,
                 paginate_by = None, page = None, allow_empty = None,
                 template_name = None, template_loader = None, extra_context = {},
                 login_required = None, context_processors = None,
                 template_object_name = None, mimetype = None, model = None,
                 lookup_kwargs = None, **kwargs):
        """
        Generic object list view function.
        """

        if queryset is None: queryset = self.queryset
        paginate_by        = paginate_by or self.paginate_by
        allow_empty        = allow_empty or self.allow_empty
        template_name      = template_name or self.template_name
        template_loader    = template_loader or self.template_loader
        extra_context      = extra_context or {}
        login_required     = login_required or self.login_required
        context_processors = context_processors or self.context_processors
        template_object_name = template_object_name or self.template_object_name
        mimetype           = mimetype or self.mimetype
        model              = model or self.model
        lookup_kwargs      = lookup_kwargs or self.lookup_kwargs

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(request)
        if extra_context is None: extra_context = {}

        queryset = queryset._clone()
        model    = model or queryset.model

        if lookup_kwargs is not None:
            filter_kwargs = {}
            for k, v in lookup_kwargs.items():
                if k in kwargs:
                    filter_kwargs[k] = kwargs[k]
            queryset = queryset.filter(**filter_kwargs)

        if paginate_by:
            paginator = self.paginator(request, queryset, paginate_by, allow_empty)
            page = self.page(request, page)
            try:
                page_number = int(page)
            except ValueError:
                if page == 'last':
                    page_number = paginator.num_pages
                else:
                    # Page is not 'last', nor can it be converted to an int.
                    raise Http404
            try:
                page_obj = paginator.page(page_number)
            except InvalidPage:
                raise Http404

            c = self.get_context(request, {
                '%s_list' % template_object_name: page_obj.object_list,
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
                }, context_processors)
        else:
            c = self.get_context(request, {
                '%s_list' % template_object_name: queryset,
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                }, context_processors)
            if not allow_empty and len(queryset) == 0:
                raise Http404
        extra_context = self.apply_extra_context(extra_context, self.extra_context)
        c = self.apply_extra_context(c, extra_context)
        c = self.append_to_context(c, request, model)
        t = self.get_template(model, template_name, template_loader)
        response = self.get_response(t, c, mimetype)
        return response

    def get_template(self, model, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        template_name   = template_name or self.template_name
        template_loader = template_loader or self.template_loader
        app_label   = model._meta.app_label
        object_name = model._meta.object_name.lower()
        template_name = template_name or ("%s/%s_list.html" % (app_label, object_name),
                                          "%s/object_list.html" % app_label,
                                          "%s_list.html" % object_name,
                                          "object_list.html")
        return super(ListObjectView, self).get_template(model, template_name, template_loader)

# ------------------------------------------------------------------------
#   FUNCTIONAL GENERIC VIEWS
# ------------------------------------------------------------------------

create_object = CreateObjectView()
update_object = UpdateObjectView()
delete_object = DeleteObjectView()
object_detail = DetailObjectView()
object_list   = ListObjectView()
