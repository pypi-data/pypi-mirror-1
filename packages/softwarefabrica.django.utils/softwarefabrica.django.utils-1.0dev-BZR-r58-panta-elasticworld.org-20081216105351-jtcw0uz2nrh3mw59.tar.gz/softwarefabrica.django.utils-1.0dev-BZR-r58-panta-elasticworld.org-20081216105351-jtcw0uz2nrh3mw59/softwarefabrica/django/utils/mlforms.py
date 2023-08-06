# mlforms.py - multilingual forms 
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
Provides extensions to newforms form_for_model and form_for_instance
that take into account multilingual translatable fields.
"""

from django.conf.urls.defaults import *

try:
    from django import newforms as forms
except:
    from django import forms
import multilingual

def ml_save_instance(form, instance, fields=None, fail_message='saved', commit=True):
    """
    Analoguous to django.newforms.models.save_instance()

    Saves bound Form ``form``'s cleaned_data into model instance ``instance``.

    If commit=True, then the changes to ``instance`` will be saved to the
    database. Returns ``instance``.
    """
    from django.db import models

    model = instance.__class__
    opts = instance.__class__._meta
    if form.errors:
        raise ValueError("The %s could not be %s because the data didn't validate." % (opts.object_name, fail_message))

    ml_fields = ml_make_fields(model)

    cleaned_data = form.cleaned_data
    for f in opts.fields + ml_fields:
        if not f.editable or isinstance(f, models.AutoField) or not f.name in cleaned_data:
            continue
        if fields and f.name not in fields:
            continue
        f.save_form_data(instance, cleaned_data[f.name])        
    # Wrap up the saving of m2m data as a function
    def save_m2m():
        opts = instance.__class__._meta
        cleaned_data = form.cleaned_data
        for f in opts.many_to_many:
            if fields and f.name not in fields:
                continue
            if f.name in cleaned_data:
                f.save_form_data(instance, cleaned_data[f.name])
    if commit:
        # If we are committing, save the instance and the m2m data immediately
        instance.save()
        save_m2m()
    else:
        # We're not committing. Add a method to the form to allow deferred 
        # saving of m2m data
        form.save_m2m = save_m2m
    return instance

def make_model_save(model, fields, fail_message):
    "Returns the save() method for a Form."
    def save(self, commit=True):
        return ml_save_instance(self, model(), fields, fail_message, commit)
    return save
    
def make_instance_save(instance, fields, fail_message):
    "Returns the save() method for a Form."
    def save(self, commit=True):
        return ml_save_instance(self, instance, fields, fail_message, commit)
    return save

def ml_language_ids():
    from multilingual.languages import get_language_id_list
    return get_language_id_list()

def ml_language_codes():
    from multilingual.languages import get_language_code_list
    return get_language_code_list()

def ml_translatable_fields(model):
    from multilingual.languages import get_language_id_list, get_language_code
    import copy

    opts = model._meta

    translatable_fields = []
    trans_model  = opts.translation_model
    trans_fields = trans_model._meta.translated_fields
    for k in trans_fields:
        (fld, lang_id) = trans_fields[k]
        if lang_id == None:
            translatable_fields.append(fld)
    return translatable_fields

def ml_translated_fields(model):
    from multilingual.languages import get_language_id_list, get_language_code
    import copy

    translatable_fields = ml_translatable_fields(model)

    translated_fields = []
    for fld in translatable_fields:
        fname = fld.name
        for language_id in get_language_id_list():
            language_code = get_language_code(language_id)
            fname_lng = fname + '_' + language_code
            field_lng = copy.copy(fld)
            field_lng.attname = fname_lng
            field_lng.name    = fname_lng
            field_lng.help_text = language_code
            translated_fields.append(field_lng)
    return translated_fields

def ml_make_fields(model):
    return ml_translated_fields(model)

def ml_order_fields(model, fieldorder=None):
    opts = model._meta

    ml_t_fields = ml_translatable_fields(model)
    ml_fields   = ml_make_fields(model)

    def find_field(flist, fname):
        for fld in flist:
            if fld.name == fname:
                return fld
        return None

    def find_field_pos(flist, fname):
        i = 0
        for fld in flist:
            if fld.name == fname:
                return i
            i += 1
        raise ValueError

    all_fields = opts.fields + ml_t_fields + ml_fields + opts.many_to_many

    all_fields_ordered = opts.fields + ml_fields + opts.many_to_many

    if fieldorder == None:
        return all_fields_ordered

    ml_t_field_names = map(lambda f: f.name, ml_t_fields)
    for (fn_pre, fn_post) in fieldorder:
        f_pre = find_field(all_fields, fn_pre)
        if fn_post in ml_t_field_names:
            fn_post_list = []
            for l_code in ml_language_codes():
                fn_post_list.append(fn_post + '_' + l_code)
        else:
            fn_post_list = [fn_post]

        i_pres = []
        try:
            i_pres.append(find_field_pos(all_fields_ordered, fn_pre))
        except ValueError:
            pass
        for l_code in ml_language_codes():
            fn = fn_pre + '_' + l_code
            try:
                i_pre = find_field_pos(all_fields_ordered, fn)
                i_pres.append(i_pre)
            except ValueError:
                continue
        i_pre = max(i_pres)
        dst = i_pre + 1
        for fn_post in fn_post_list:
            f_post = find_field(all_fields, fn_post)
            try:
                i_post = find_field_pos(all_fields_ordered, fn_post)
            except ValueError:
                continue
            del all_fields_ordered[i_post]
            all_fields_ordered.insert(dst, f_post)
            dst += 1
    return all_fields_ordered

def ml_form_for_model(model, form=forms.BaseForm, fields=None, formfield_callback=lambda f: f.formfield(), fieldorder=None):
    """
    Returns a Form class for the given Django model class.

    Provide ``form`` if you want to use a custom BaseForm subclass.

    Provide ``formfield_callback`` if you want to define different logic for
    determining the formfield for a given database field. It's a callable that
    takes a database Field instance and returns a form Field instance.
    """
    from forms.forms  import SortedDictFromList

    opts = model._meta

    all_fields_ordered = ml_order_fields(model, fieldorder)

    field_list = []
    for f in all_fields_ordered:
        if not f.editable:
            continue
        if fields and not f.name in fields:
            continue
        formfield = formfield_callback(f)
        if formfield:
            field_list.append((f.name, formfield))
    base_fields = SortedDictFromList(field_list)
    return type(opts.object_name + 'Form', (form,), 
        {'base_fields': base_fields, '_model': model, 'save': make_model_save(model, fields, 'created')})

def ml_form_for_instance(instance, form=forms.BaseForm, fields=None, formfield_callback=lambda f, **kwargs: f.formfield(**kwargs), fieldorder=None):
    """
    Returns a Form class for the given Django model instance.

    Provide ``form`` if you want to use a custom BaseForm subclass.

    Provide ``formfield_callback`` if you want to define different logic for
    determining the formfield for a given database field. It's a callable that
    takes a database Field instance, plus **kwargs, and returns a form Field
    instance with the given kwargs (i.e. 'initial').
    """
    from forms.forms  import SortedDictFromList

    model = instance.__class__
    opts = model._meta

    ml_t_fields = ml_translatable_fields(model)
    ml_fields   = ml_translated_fields(model)

    all_fields_ordered = ml_order_fields(model, fieldorder)
    
    field_list = []
    for f in all_fields_ordered:
        if not f.editable:
            continue
        if fields and not f.name in fields:
            continue

        style = None
        for l_code in ml_language_codes():
            suffix = '_' + l_code
            suffix_len = len(suffix)
            if f in ml_fields:
                if (len(f.name) > suffix_len) and (f.name[-suffix_len:] == suffix):
                    style = "trans" + suffix

        current_value = f.value_from_object(instance)
        extra_attrs = None
        if style:
            extra_attrs = {'class': style}
        formfield = formfield_callback(f, initial=current_value)
        if style and extra_attrs:
            formfield.widget.attrs.update(extra_attrs)

        if formfield:
            field_list.append((f.name, formfield))
    base_fields = SortedDictFromList(field_list)
    return type(opts.object_name + 'InstanceForm', (form,),
        {'base_fields': base_fields, '_model': model, 'save': make_instance_save(instance, fields, 'changed')})
