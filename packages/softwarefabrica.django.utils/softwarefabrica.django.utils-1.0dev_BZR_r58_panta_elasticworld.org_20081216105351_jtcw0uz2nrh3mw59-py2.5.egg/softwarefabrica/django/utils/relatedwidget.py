# relatedwidget.py - related (ForeignKey) extended widget support
# Copyright (C) 2008 Marco Pantaleoni. All rights reserved
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

from django.utils.encoding import force_unicode
from django.conf import settings
try:
    from django import newforms as forms
except:
    from django import forms
from django.template import Context, loader
from django.utils.safestring import mark_safe

from softwarefabrica.django.utils.viewshelpers import static_media_prefix, static_media_images_prefix

import types

class RelatedItemWidget(forms.widgets.TextInput):
    staticmedia = static_media_prefix()
    images = static_media_images_prefix()

    def _get_model(self):
        return self._model

    def _set_model(self, value):
        self._model = value
    model = property(_get_model, _set_model)

    def render(self, name, value, attrs=None):
        if value is None: value = ''
        tr_name = name + '_textrepr'
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        tr_attrs = self.build_attrs(attrs, type=self.input_type, name=tr_name)
        if value != '': 
            final_attrs['value'] = force_unicode(value)
        if not final_attrs.has_key('id'):
            final_attrs['id'] = u'%s_id' % (name)
        final_attrs['type'] = 'hidden'
        #for key in ('type', 'name',):
        #    if key in tr_attrs:
        #        del tr_attrs[key]
        tr_attrs['id'] = u'id_%s' % (tr_name)
        id = final_attrs['id']

        model = self.model
        opts  = model._meta

        obj = None
        #obj_repr = u'--'
        obj_repr = u''
        if model and value:
            obj = model.objects.get(id = long(value))
        if obj:
            obj_repr = force_unicode(obj)
        tr_attrs['value'] = obj_repr

        t = loader.get_template('utils/widget/foreign.html')
        c = Context({'images':		self.images,
                     'model':		model,
                     'opts':		opts,
                     'model_name':	opts.object_name.lower(),
                     'id':		id,
                     'value':           value,
                     'obj':             obj,
                     'obj_repr':        obj_repr,
                     'tr_attrs':	mark_safe(forms.util.flatatt(tr_attrs)),
                     'attrs':		mark_safe(forms.util.flatatt(final_attrs))})
        return mark_safe(t.render(c))

    def value_from_datadict(self, data, files, name):
        empty_values = forms.fields.EMPTY_VALUES

        value = data.get(name, None)
        if value in empty_values:
            return None
        if isinstance(value, (types.NoneType, int, long)):
            return value
        if isinstance(value, (str, unicode)):
            return long(value)
        return None

class SelectModelField(forms.ModelChoiceField):
    """
    An input field to select from a model QuerySet.
    This derives from (new)forms.ModelChoiceField but using the
    RelatedItemWidget to allow selecting with a popup interface.
    """
    widget = RelatedItemWidget

    def __init__(self, queryset, empty_label=u"---------", cache_choices=False,
                 required=False, widget=RelatedItemWidget, label=None, initial=None,
                 help_text=None, *args, **kwargs):
        super(SelectModelField, self).__init__(queryset, empty_label, cache_choices,
                                               required, widget, label, initial, help_text,
                                               *args, **kwargs)
        self.widget.model = queryset.model
