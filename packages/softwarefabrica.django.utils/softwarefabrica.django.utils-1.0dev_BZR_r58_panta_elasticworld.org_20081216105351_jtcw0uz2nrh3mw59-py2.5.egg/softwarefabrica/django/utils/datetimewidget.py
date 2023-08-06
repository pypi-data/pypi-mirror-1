#
# DateTimeWidget
#
# JavaScript Django form widget to display a nice calendar for DateTime
# form fields.
#
# This widget uses: DHTML Calendar Widget. It is very simple implementation but
# may be easily extended/changed/refined.  Necessary files: First download
# calendar package and extract it to your MEDIA folder (MEDIA/calendar/...) You'll
# also need a small gif that will be shown as a button that allows user to display
# calendar. By default this 'gif' is searched at '[MEDIA]images/calbutton.gif' but
# you may change this path in the code (calbtn variable). You need to download or
# create callbutton.gif image by yourself (it is not included).  Include css and
# js files in your page (as shown in the comment in the code).  In form code
# assign a widget to a field as usual (see newforms documentation for more
# details).  It is possible to change date format by specifying different value
# for 'dformat' attribute of widget class.  If you get javascript errors while
# trying to open calendar try to use english translation file
# (calendar-en.js). I've found that some translations, eg. Polish, are broken by
# default. In this case you should override your language translation with english
# one and translate it by yourself (it is easy).
#
# DHTML Calendar Widget:
#   http://www.dynarch.com/projects/calendar/
#   http://prdownloads.sourceforge.net/jscalendar/jscalendar-1.0.zip?download
#
# adapted from:
#   http://www.djangosnippets.org/snippets/391/
#
# Modifications on the original are:
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

from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.conf import settings
try:
    from django import newforms as forms
    from django.newforms import fields
    from django.newforms import widgets
except:
    from django import forms
    from django.forms import fields
    from django.forms import widgets
#from datetime import datetime
import datetime
import time

from softwarefabrica.django.utils.viewshelpers import static_media_prefix

# DATETIMEWIDGET
#calbtn = u"""<img src="%s/images/icon_calendar.gif" alt="calendar" id="%s_btn" style="cursor: pointer; border: 1px solid #8888aa;" title="Select date and time"
#            onmouseover="this.style.background='#444444';" onmouseout="this.style.background=''" />
calbtn = u"""<img src="%s/images/icon_calendar.gif" alt="calendar" id="%s_btn" style="cursor: pointer;" title="Select date and time" />
<script type="text/javascript">
    Calendar.setup({
        inputField     :    "%s",
        ifFormat       :    "%s",
        button         :    "%s_btn",
        singleClick    :    true,
        showsTime      :    true
    });
</script>"""

class DateTimeWidget(forms.widgets.TextInput):
    staticmedia = static_media_prefix()
    #dformat = '%Y-%m-%d %H:%M'
    #dformat = '%d-%m-%Y %H:%M'
    dformat = '%d/%m/%Y %H:%M'
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '': 
            try:
                final_attrs['value'] = \
                                   force_unicode(value.strftime(self.dformat))
            except:
                final_attrs['value'] = \
                                   force_unicode(value)
        if not final_attrs.has_key('id'):
            final_attrs['id'] = u'%s_id' % (name)
        id = final_attrs['id']
        
        jsdformat = self.dformat #.replace('%', '%%')
        cal = calbtn % (self.staticmedia, id, id, jsdformat, id)
        a = u'<span class="nobreak"><span class="date"><input%s />&nbsp;%s</span></span>' % (forms.util.flatatt(final_attrs), cal)
        return mark_safe(a)

class DateTimeFieldCalendar(forms.DateTimeField):
    widget = DateTimeWidget

class DateWidget(forms.widgets.TextInput):
    staticmedia = static_media_prefix()
    #dformat = '%Y-%m-%d'
    #dformat = '%d-%m-%Y'
    dformat = '%d/%m/%Y'
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '': 
            try:
                final_attrs['value'] = \
                                   force_unicode(value.strftime(self.dformat))
            except:
                final_attrs['value'] = \
                                   force_unicode(value)
        if not final_attrs.has_key('id'):
            final_attrs['id'] = u'%s_id' % (name)
        id = final_attrs['id']

        jsdformat = self.dformat #.replace('%', '%%')
        cal = calbtn % (self.staticmedia, id, id, jsdformat, id)
        a = u'<span class="nobreak"><span class="date"><input%s />&nbsp;%s</span></span>' % (forms.util.flatatt(final_attrs), cal)
        return mark_safe(a)

class DateFieldCalendar(forms.DateField):
    widget = DateWidget

import re

date_range_re = re.compile(r'([0-9]{2}-|/[0-9]{2}-|/[0-9]{4})?\s+-\s+([0-9]{2}-|/[0-9]{2}-|/[0-9]{4})?')

class DateRangeWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (DateWidget(attrs=attrs), DateWidget(attrs=attrs))
        super(DateRangeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            m = date_range_re.match(value)
            if m:
                date1 = None
                date2 = None
                (date1_s, date2_s) = m.groups()
                if date1_s and (date1_s != ''):
                    date1 = datetime.datetime(*time.strptime(date1_s, "%d/%m/%Y")[:3])
                if date2_s and (date2_s != ''):
                    date2 = datetime.datetime(*time.strptime(date2_s, "%d/%m/%Y")[:3])
            return [date1, date2]
        return [None, None]

    def format_output(self, rendered_widgets):
        return u' - '.join(rendered_widgets)

    def render(self, name, value, attrs=None):
        r = super(DateRangeWidget, self).render(name, value, attrs=attrs)
        return mark_safe(u'<span class="daterange">%s</span>' % r)
        #return r

try:
    from django.newforms.util import ErrorList, ValidationError
    from django.newforms.fields import EMPTY_VALUES
except:
    from django.forms.util import ErrorList, ValidationError
    from django.forms.fields import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import StrAndUnicode, smart_unicode, smart_str

class DateRangeField(fields.Field):
    widget = DateRangeWidget
    default_error_messages = {
        'invalid': _(u'Enter a valid date range.'),
    }

    def __init__(self, input_formats=None, *args, **kwargs):
        super(DateRangeField, self).__init__(*args, **kwargs)
        self.input_formats = input_formats or DEFAULT_DATE_INPUT_FORMATS

    def clean(self, value):
        """
        Validates that the input can be converted to a datetime or datetime pair.
        Returns a Python datetime.datetime object or pair.
        """
        super(DateRangeField, self).clean(value)
        if value in EMPTY_VALUES:
            return None
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            return datetime.datetime(value.year, value.month, value.day)
        if isinstance(value, list):
            # Input comes from a DateRangeWidget
            if len(value) != 2:
                raise ValidationError(self.error_messages['invalid'])
            (date1, date2) = (None, None)
            (date1_v, date2_v) = value
            if (type(date1_v) == type('')) or (type(date1_v) == type(u'')) and date1_v and (date1_v != ''):
                date1 = datetime.datetime(*time.strptime(date1_v, "%d/%m/%Y")[:3])
            if (type(date2_v) == type('')) or (type(date2_v) == type(u'')) and date2_v and (date2_v != ''):
                date2 = datetime.datetime(*time.strptime(date2_v, "%d/%m/%Y")[:3])
            #value = '%s - %s' % tuple(value)
            value = (date1, date2)
            return value
        try:
            date1 = None
            date2 = None
            m = date_range_re.match(value)
            if m:
                (date1_s, date2_s) = m.groups()
                if date1_s and (date1_s != ''):
                    date1 = datetime.datetime(*time.strptime(date1_s, "%d/%m/%Y")[:3])
                if date2_s and (date2_s != ''):
                    date2 = datetime.datetime(*time.strptime(date2_s, "%d/%m/%Y")[:3])
            return (date1, date2)
        except ValueError:
            raise ValidationError(self.error_messages['invalid'])
