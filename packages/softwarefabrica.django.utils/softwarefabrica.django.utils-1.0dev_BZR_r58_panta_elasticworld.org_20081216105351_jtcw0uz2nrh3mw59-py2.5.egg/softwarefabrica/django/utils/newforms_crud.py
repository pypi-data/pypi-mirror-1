# newforms_crud.py - CRUD forms support
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

from django.core.xheaders import populate_xheaders
from django.template import loader
from django.contrib.auth.views import redirect_to_login
from django.template import RequestContext
from django.db.models import FileField
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.utils.translation import gettext
try:
    from django import newforms as newforms
except:
    from django import forms as newforms
import forms

        
"""
Rewrites of create_object and update_object generic views, modified to use newforms.
Some other changes:
- extra_fields : this can be a dict, or callable returning a dict:
    def extra_fields(request, object = None) (object passed to callable in update_object)
  This allows passing in of non-form fields, for example the current user id, e.g.
  extra_fields = { "author" : request.user }
- base_form, formfield_callback - optional arguments passed to form_for_model and form_for_instance.
- on_success - callback called after successful save:
    def on_success(request, form, object)
  If on_success is not set, a redirect is returned
- on_failure - callback called if form is invalid:
    def on_failure(request, form, object = None) (object passed to callable in update_object)
  If on_failure is not set, form template is displayed with errors.

Example:

class Project(models.Model):
    name = models.CharField(maxlength = 50)
    description = models.TextField()
    owner = models.ForeignKey(User, editable = False)

def add_project(request):

    return create_object(request, Project, on_success = on_create_project,
        extra_fields = {"owner" : request.user})
        
def on_create_project(request, form, project):

    request.session["flash"] = "Project %s created!" %project.name
    return HttpResponseRedirect("/")
    
"""

def save_file_fields(new_data, object):

    for f in object._meta.fields:
        if f.name in new_data and isinstance(f, FileField):
            upload_data = new_data.get(f.name, False)
            if upload_data:
                func = getattr(object, 'save_%s_file' % f.name)
                func(upload_data["filename"],upload_data["content"], False)
           
def create_object(request, model, template_name=None,
                  base_form = None, formfield_callback = None, extra_fields = None,
                  template_loader=loader, extra_context=None, post_save_redirect=None,
                  login_required=False, context_processors=None, 
                  on_success = None, on_failure=None,
                  initial = None):
    
    """
    Generic object-creation function.

    Templates: ``<app_label>/<model_name>_form.html``
    Context:
        form
            the form wrapper for the object
    """
    if extra_context is None: extra_context = {}
    if login_required and not request.user.is_authenticated():
        return redirect_to_login(request.path)
    
    #if base_form is None : base_form = newforms.BaseForm
    if formfield_callback is None : formfield_callback = lambda f, **kw : f.formfield(**kw)

    form = forms.form_for_model(model=model, form=base_form, formfield_callback=formfield_callback)
    
    if request.POST or request.FILES:
        # If data was POSTed, we're trying to create a new object
        new_data = request.POST.copy()

        if request.FILES:
            new_data.update(request.FILES)

        if initial != None:
            form = form(new_data, initial = initial)
        else:
            form = form(new_data)
        
        if form.is_valid():
            
            # No errors -- this means we can save the data!
            if callable(extra_fields) : extra_fields = extra_fields(request)
            
            if extra_fields is None : extra_fields = {}
                                
            if extra_fields or request.FILES:
                new_object = form.save(commit = False)
                for k, v in extra_fields.items():
                    setattr(new_object, k, v)
                save_file_fields(new_data, new_object)
                new_object.save()
            else:
                new_object = form.save(commit = True)
                
            if callable(on_success):
                return on_success(request, form, new_object)
            else:   

                if request.user.is_authenticated():
                    request.user.message_set.create(message=gettext("The %(verbose_name)s was created successfully.") % {"verbose_name": model._meta.verbose_name})

                # Redirect to the new object: first by trying post_save_redirect,
                # then by obj.get_absolute_url; fail if neither works.
                if post_save_redirect:
                    return HttpResponseRedirect(post_save_redirect % new_object.__dict__)
                elif hasattr(new_object, 'get_absolute_url'):
                    return HttpResponseRedirect(new_object.get_absolute_url())
                else:
                    raise ImproperlyConfigured("No URL to redirect to from generic create view.")
        else:
        
            if callable(on_failure): return on_failure(request, form)
    else:
        # No POST, so we want a brand new form without any data or errors
        if initial != None:
            form = form(initial = initial)
        else:
            form = form()

    if not template_name:
        template_name = "%s/%s_form.html" % (model._meta.app_label, model._meta.object_name.lower())
    t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        'form': form,
    }, context_processors)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c))

def update_object(request, model, object_id=None, slug=None,
                  slug_field=None, template_name=None, template_loader=loader,
                  extra_context=None, post_save_redirect=None, extra_fields = None,
                  login_required=False, context_processors=None,
                  base_form = None, formfield_callback = None,
                  on_success = None, on_failure = None,
                  template_object_name='object',
                  initial = None):
    """
    Generic object-update function.

    Templates: ``<app_label>/<model_name>_form.html``
    Context:
        form
            the form wrapper for the object
        object
            the original object being edited
    """
    if extra_context is None: extra_context = {}
    if login_required and not request.user.is_authenticated():
        return redirect_to_login(request.path)

    # Look up the object to be edited
    lookup_kwargs = {}
    if object_id:
        lookup_kwargs['%s__exact' % model._meta.pk.name] = object_id
    elif slug and slug_field:
        lookup_kwargs['%s__exact' % slug_field] = slug
    else:
        raise AttributeError("Generic edit view must be called with either an object_id or a slug/slug_field")
    try:
        object = model.objects.get(**lookup_kwargs)
    except ObjectDoesNotExist:
        raise Http404, "No %s found for %s" % (model._meta.verbose_name, lookup_kwargs)

    #if base_form is None : base_form = newforms.BaseForm
    if formfield_callback is None : formfield_callback = lambda f, **kw : f.formfield(**kw)

    form = forms.form_for_instance(instance=object, form=base_form, formfield_callback=formfield_callback)
    
    if request.POST or request.FILES:
        # If data was POSTed, we're trying to create a new object
        new_data = request.POST.copy()

        if request.FILES:
            new_data.update(request.FILES)
        if initial != None:
            form = form(new_data, initial = initial)
        else:
            form = form(new_data)
    
        if form.is_valid():
            # No errors -- this means we can save the data!
            if callable(extra_fields) : extra_fields = extra_fields(request, object)
            
            if extra_fields or request.FILES:
                form.save(commit = False)
                for k, v in extra_fields.items():
                    setattr(object, k, v)
                save_file_fields(new_data, object)
                object.save()
            else:
                form.save(commit = True)

            if callable(on_success):

                return on_success(request, form, object)

            else:   

                if request.user.is_authenticated():
                    request.user.message_set.create(message=gettext("The %(verbose_name)s was updated successfully.") % {"verbose_name": model._meta.verbose_name})

                # Do a post-after-redirect so that reload works, etc.
                if post_save_redirect:
                    return HttpResponseRedirect(post_save_redirect % object.__dict__)
                elif hasattr(object, 'get_absolute_url'):
                    return HttpResponseRedirect(object.get_absolute_url())
                else:
                    raise ImproperlyConfigured("No URL to redirect to from generic create view.")

    else:
        if initial != None:
            form = form(initial = initial)
        else:
            form = form()    
        if callable(on_failure) : return on_failure(request, form, object)
        
    if not template_name:
        template_name = "%s/%s_form.html" % (model._meta.app_label, model._meta.object_name.lower())
    t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        'form': form,
        template_object_name: object,
    }, context_processors)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    response = HttpResponse(t.render(c))
    populate_xheaders(request, response, model, getattr(object, object._meta.pk.attname))
    return response

