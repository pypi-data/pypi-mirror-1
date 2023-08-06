# forms.py - form handling
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

from django.template import Context, loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.conf.urls.defaults import *
from django.contrib.auth import logout
try:
    from django import newforms as forms
except:
    from django import forms

from django.conf import settings

try:
    from mlforms import ml_form_for_model as p_form_for_model, ml_form_for_instance as p_form_for_instance
except ImportError:
    try:
        from django.newforms.models import form_for_model as o_form_for_model, form_for_instance as o_form_for_instance
    except:
        from django.forms.models import form_for_model as o_form_for_model, form_for_instance as o_form_for_instance
    def p_form_for_model(model, form=forms.BaseForm, fields=None, formfield_callback=None, fieldorder=None):
        return o_form_for_model(model=model, form=form, fields=fields, formfield_callback=formfield_callback)
    def p_form_for_instance(instance, form=forms.BaseForm, fields=None, formfield_callback=None, fieldorder=None):
        return o_form_for_instance(instance=instance, form=form, fields=fields, formfield_callback=formfield_callback)

class ExtForm(forms.BaseForm):
    def _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        "Helper function for outputting HTML. Used by as_table(), as_ul(), as_p()."
        from forms.forms import BoundField
        from forms.fields import Field
        from forms.util import flatatt, ErrorDict, ErrorList, ValidationError
        from django.utils.html import escape
        from django.utils.encoding import StrAndUnicode, smart_unicode, force_unicode
        from django.utils.safestring import mark_safe
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []
        for name, field in self.fields.items():
            bf = BoundField(self, field, name)
            bf_errors = self.error_class([escape(error) for error in bf.errors]) # Escape and cache in local variable.
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend(['(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                if errors_on_separate_row and bf_errors:
                    output.append(error_row % force_unicode(bf_errors))
                if bf.label:
                    label = escape(force_unicode(bf.label))
                    # Only add the suffix if the label does not end in punctuation.
                    if self.label_suffix:
                        if label[-1] not in ':?.!':
                            label += self.label_suffix
                    if field.required:
                        label = bf.label_tag(label, attrs={'class': 'required'}) or ''
                    else:
                        label = bf.label_tag(label, attrs={'class': 'optional'}) or ''
                else:
                    label = ''
                if field.help_text:
                    help_text = help_text_html % force_unicode(field.help_text)
                else:
                    help_text = u''
                output.append(normal_row % {'errors': force_unicode(bf_errors), 'label': force_unicode(label), 'field': unicode(bf), 'help_text': help_text})
        if top_errors:
            output.insert(0, error_row % top_errors)
        if hidden_fields: # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and insert the hidden fields.
                output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
            else: # If there aren't any rows in the output, just append the hidden fields.
                output.append(str_hidden)
        return mark_safe(u'\n'.join(output))

def ext_callback(field, fallback=None, **kwargs):
    import datetimewidget
    from django.db import models

    kwargs['required'] = not field.blank
    if isinstance(field, models.DateField):
        return datetimewidget.DateFieldCalendar(**kwargs)
    if isinstance(field, models.DateTimeField):
        return datetimewidget.DateTimeFieldCalendar(**kwargs)
    elif fallback != None:
        return fallback(field, **kwargs)
    else:
        return field.formfield(**kwargs)

def form_for_model(model, form=None, fields=None, formfield_callback=None, fieldorder=None):
    """
    Extends django.newforms.models.form_for_model by:
       - returning a DHTML Calendar for DateTimeField fields
    """
    from forms import models

    formfield_callback_original = lambda f: f.formfield()

    if form == None:
        form = ExtForm

    if formfield_callback:
        #return models.form_for_model(model, form, fields, formfield_callback=lambda f, cb=ext_callback, fb=formfield_callback: cb(f, fb))
        return p_form_for_model(model, form, fields, formfield_callback=lambda f, cb=ext_callback, fb=formfield_callback: cb(f, fb), fieldorder=fieldorder)
    #return models.form_for_model(model, form, fields, formfield_callback=ext_callback)
    return p_form_for_model(model, form, fields, formfield_callback=ext_callback, fieldorder=fieldorder)

def form_for_instance(instance, form=None, fields=None, formfield_callback=None, fieldorder=None):
    """
    Extends django.newforms.models.form_for_instance by:
       - returning a DHTML Calendar for DateTimeField fields
    """
    from forms import models

    formfield_callback_original = lambda f, **kwargs: f.formfield(**kwargs)

    if form == None:
        form = ExtForm

    if formfield_callback:
        #return form_for_instance(instance, form, fields,
        #                             formfield_callback=lambda f, cb=ext_callback, fb=formfield_callback, **kwargs: cb(f, fb, **kwargs))
        return p_form_for_instance(instance, form, fields,
                                   formfield_callback=lambda f, cb=ext_callback, fb=formfield_callback, **kwargs: cb(f, fb, **kwargs), fieldorder=fieldorder)
    #return form_for_instance(instance, form, fields, formfield_callback=lambda f, cb=ext_callback, **kwargs: cb(f, None, **kwargs))
    return p_form_for_instance(instance, form, fields, formfield_callback=lambda f, cb=ext_callback, **kwargs: cb(f, None, **kwargs), fieldorder=fieldorder)

