# Copyright (C) 2008-2010 Marco Pantaleoni. All rights reserved
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
from django.template import Context, RequestContext, loader
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from django.conf import settings

try:
    from django import newforms as forms
    from django.newforms import fields
    from django.newforms import widgets
except:
    from django import forms
    from django.forms import fields
    from django.forms import widgets

import datetime
import time

reverse_lazy = lazy(reverse, unicode)

class WidgetHelper(object):
    """
    Support for enhanced functionalities in widgets, such as template-based
    rendering.

    This is not a base class, mainly to avoid problems with multiple-inheritance,
    in particular with super (see http://fuhm.net/super-harmful/).
    """

    TEMPLATE_NAME   = None
    TEMPLATE_LOADER = loader

    def __init__(self, widget, *args, **kwargs):
        super(WidgetHelper, self).__init__(*args, **kwargs)
        template_name   = kwargs.pop('template_name',
                                     getattr(widget, 'template_name',
                                             getattr(widget, 'TEMPLATE_NAME', self.TEMPLATE_NAME)))
        template_loader = kwargs.pop('template_loader',
                                     getattr(widget, 'template_loader',
                                             getattr(widget, 'TEMPLATE_LOADER', self.TEMPLATE_LOADER)))
        self.widget          = widget
        self.template_name   = template_name
        self.template_loader = template_loader
        self.widget.widget_helper = self

    def render(self, name, value, attrs=None, base_dict={}, *args, **kwargs):
        if hasattr(self.widget, 'render_base'):
            html = self.widget.render_base(name, value, attrs=attrs, *args, **kwargs)
        else:
            html = ''
        c = self.get_context(base_dict, name, value, attrs, html, *args, **kwargs)
        t = self.get_template()
        return self.render_output(t, c)

    def get_context(self, base_dict, name, value, attrs, base_widget, *args, **kwargs):
        if hasattr(self.widget, 'get_context'):
            return self.widget.get_context(base_dict, name, value, attrs, base_widget, *args, **kwargs)
        d = self.get_context_dict(base_dict, name, value, attrs, base_widget, *args, **kwargs)
        return Context(d)

    def get_context_dict(self, base_dict, name, value, attrs, base_widget, *args, **kwargs):
        if value is None: value = ''
        widget_id = self.get_widget_id(name, attrs)
        d = dict(base_dict,
                 basewidget = mark_safe(base_widget),
                 field      = mark_safe(name),
                 id         = widget_id)
        if hasattr(self.widget, 'get_context_dict'):
            base_dict_new = base_dict.copy()
            base_dict_new.update(d)
            return self.widget.get_context_dict(base_dict_new, name, value, attrs, base_widget, *args, **kwargs)
        return d

    def get_widget_id(self, name, attrs):
        if hasattr(self.widget, 'get_widget_id'):
            return self.widget.get_widget_id(name, attrs)
        widget_id = ''
        if attrs and attrs.has_key('id'):
            widget_id = attrs['id']
        else:
            widget_id = u'%s_id' % (name)
        return widget_id

    def get_template(self, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        if hasattr(self.widget, 'get_template'):
            return self.widget.get_template(template_name, template_loader)
        template_name   = template_name or self.template_name
        template_loader = template_loader or self.template_loader
        if isinstance(template_name, (list, tuple)):
            return template_loader.select_template(template_name)
        else:
            return template_loader.get_template(template_name)

    def render_output(self, template, context_instance):
        if hasattr(self.widget, 'render_output'):
            return self.widget.render_output(template, context_instance)
        return template.render(context_instance)

class NullBooleanSelect(widgets.NullBooleanSelect):
    """
    A Select Widget intended to be used with NullBooleanField.

    This fixes the Django NullBooleanSelect widget problem with FormWizard and
    FormPreview.

    This avoids Django bug #9473:
    http://code.djangoproject.com/ticket/9473
    """

    def render(self, name, value, attrs=None, choices=()):
        try:
            value = {True: u'2', False: u'3', u'2': u'2', u'3': u'3',
                     u'True': u'2', u'False': u'3'}[value]
        except KeyError:
            value = u'1'
        return super(NullBooleanSelect, self).render(name, value, attrs, choices)

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        return {u'2': True, u'3': False, True: True, False: False,
                u'True': True, u'False': False}.get(value, None)

class DateTimeWidget(forms.widgets.TextInput):
    """
    A widget for forms.DateTimeField fields with a button and a
    nice JavaScript popup calendar.
    """

    #DATE_FORMAT     = '%Y-%m-%d %H:%M'
    #DATE_FORMAT     = '%d-%m-%Y %H:%M'
    DATE_FORMAT     = '%d/%m/%Y %H:%M'
    TEMPLATE_NAME   = "forms/widgets/datetime.html"
    TEMPLATE_LOADER = loader

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'input_formats'):
            self.DATE_FORMAT = self.input_formats[0]
        date_format     = kwargs.pop('date_format', self.DATE_FORMAT)
        template_name   = kwargs.pop('template_name', self.TEMPLATE_NAME)
        template_loader = kwargs.pop('template_loader', self.TEMPLATE_LOADER)
        super(DateTimeWidget, self).__init__(*args, **kwargs)
        self.date_format     = date_format
        self.template_name   = template_name
        self.template_loader = template_loader
        self.widget_helper = WidgetHelper(self, *args, **kwargs)

    def render_base(self, name, value, attrs=None, *args, **kwargs):
        return super(DateTimeWidget, self).render(name, value, attrs, *args, **kwargs)

    def render(self, name, value, attrs=None):
        return self.widget_helper.render(name, value, attrs=attrs)

    def get_context_dict(self, base_dict, name, value, attrs, base_widget, *args, **kwargs):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '': 
            try:
                final_attrs['value'] = \
                                   force_unicode(value.strftime(self.get_date_format()))
            except:
                final_attrs['value'] = \
                                   force_unicode(value)
        if not final_attrs.has_key('id'):
            final_attrs['id'] = u'%s_id' % (name)
        id = final_attrs['id']
        
        jsdformat = self.get_date_format() #.replace('%', '%%')

        return dict(base_dict,
                    flatattrs = mark_safe(forms.util.flatatt(final_attrs)),
                    attrs     = final_attrs,
                    id        = id,
                    ifFormat  = jsdformat)

    def get_date_format(self):
        return self.date_format

class DateWidget(forms.widgets.TextInput):
    """
    A widget for forms.DateField fields with a button and a
    nice JavaScript popup calendar.
    """

    #DATE_FORMAT     = '%Y-%m-%d'
    #DATE_FORMAT     = '%d-%m-%Y'
    DATE_FORMAT     = '%d/%m/%Y'
    TEMPLATE_NAME   = "forms/widgets/date.html"
    TEMPLATE_LOADER = loader

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'input_formats'):
            self.DATE_FORMAT = self.input_formats[0]
        date_format     = kwargs.pop('date_format', self.DATE_FORMAT)
        template_name   = kwargs.pop('template_name', self.TEMPLATE_NAME)
        template_loader = kwargs.pop('template_loader', self.TEMPLATE_LOADER)
        super(DateWidget, self).__init__(*args, **kwargs)
        self.date_format     = date_format
        self.template_name   = template_name
        self.template_loader = template_loader
        self.widget_helper = WidgetHelper(self, *args, **kwargs)

    def render_base(self, name, value, attrs=None, *args, **kwargs):
        return super(DateWidget, self).render(name, value, attrs, *args, **kwargs)

    def render(self, name, value, attrs=None):
        return self.widget_helper.render(name, value, attrs=attrs)

    def get_context_dict(self, base_dict, name, value, attrs, base_widget, *args, **kwargs):
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

        jsdformat = self.get_date_format() #.replace('%', '%%')

        return dict(base_dict,
                    flatattrs = mark_safe(forms.util.flatatt(final_attrs)),
                    attrs     = final_attrs,
                    id        = id,
                    ifFormat  = jsdformat)

    def get_date_format(self):
        return self.date_format

import re

date_range_re = re.compile(r'([0-9]{2}-|/[0-9]{2}-|/[0-9]{4})?\s+-\s+([0-9]{2}-|/[0-9]{2}-|/[0-9]{4})?')

class DateRangeWidget(widgets.MultiWidget):
    """
    A widget for date ranges, with buttons and nice JavaScript
    popup calendars.
    """

    DATE_FORMAT     = '%d/%m/%Y'

    def __init__(self, attrs=None, **kwargs):
        input_formats = (self.DATE_FORMAT,)
        if hasattr(self, 'input_formats'):
            input_formats = self.input_formats
        date_format = kwargs.pop('date_format', None)
        widgets = (DateWidget(attrs=attrs, date_format=date_format), DateWidget(attrs=attrs, date_format=date_format))
        widgets[0].input_formats = input_formats
        widgets[1].input_formats = input_formats
        super(DateRangeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            m = date_range_re.match(value)
            if m:
                date1 = None
                date2 = None
                (date1_s, date2_s) = m.groups()
                if date1_s and (date1_s != ''):
                    date1 = datetime.datetime(*time.strptime(date1_s, DateWidget.DATE_FORMAT)[:3])
                if date2_s and (date2_s != ''):
                    date2 = datetime.datetime(*time.strptime(date2_s, DateWidget.DATE_FORMAT)[:3])
            return [date1, date2]
        return [None, None]

    def format_output(self, rendered_widgets):
        return u' - '.join(rendered_widgets)

    def render(self, name, value, attrs=None):
        r = super(DateRangeWidget, self).render(name, value, attrs=attrs)
        return mark_safe(u'<span class="daterange">%s</span>' % r)
        #return r

import types

class RelatedItemWidget(forms.widgets.TextInput):
    """
    A widget for ForeignKey fields that allows the selection of an
    object (model instance) from a QuerySet using a popup interface.

    This widget uses a TextInput as the underlying interface, with an
    additional set of buttons.

    See the companion softwarefabrica.django.forms.fields.RelatedItemField
    form field.
    """

    TEMPLATE_NAME   = "forms/widgets/relateditem.html"
    TEMPLATE_LOADER = loader

    def _get_model(self):
        return self._model

    def _set_model(self, value):
        self._model = value
    model = property(_get_model, _set_model)

    def __init__(self, *args, **kwargs):
        template_name   = kwargs.pop('template_name', self.TEMPLATE_NAME)
        template_loader = kwargs.pop('template_loader', self.TEMPLATE_LOADER)
        super(RelatedItemWidget, self).__init__(*args, **kwargs)
        self.template_name   = template_name
        self.template_loader = template_loader
        self.widget_helper = WidgetHelper(self, *args, **kwargs)

    def render_base(self, name, value, attrs=None, *args, **kwargs):
        return super(RelatedItemWidget, self).render(name, value, attrs, *args, **kwargs)

    def render(self, name, value, attrs=None):
        return self.widget_helper.render(name, value, attrs=attrs)

    def get_context_dict(self, base_dict, name, value, attrs, base_widget, *args, **kwargs):
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

        return dict(base_dict,
                    model		= model,
                    opts		= opts,
                    model_name		= mark_safe(opts.object_name.lower()),
                    id			= id,
                    value               = value,
                    obj                 = obj,
                    obj_repr            = mark_safe(obj_repr),
                    tr_attrs            = mark_safe(forms.util.flatatt(tr_attrs)),
                    attrs               = mark_safe(forms.util.flatatt(final_attrs)))

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

class SelectPopupWidget(forms.Select):
    """
    A widget for ForeignKey fields that allows the selection of an
    object (model instance) from a QuerySet using a popup interface.

    This widget uses a Select as the underlying interface, with an
    additional set of buttons.

    See the companion softwarefabrica.django.forms.fields.SelectPopupField
    form field.
    """

    TEMPLATE_NAME   = "forms/widgets/select-popup.html"
    TEMPLATE_LOADER = loader

    def __init__(self, model, attrs=None, choices=(), *args, **kwargs):
        template_name   = kwargs.pop('template_name', self.TEMPLATE_NAME)
        template_loader = kwargs.pop('template_loader', self.TEMPLATE_LOADER)
        super(SelectPopupWidget, self).__init__(attrs, choices, *args, **kwargs)
        self.template_name   = template_name
        self.template_loader = template_loader
        self.model = model
        self.widget_helper = WidgetHelper(self, *args, **kwargs)

    def render_base(self, name, value, attrs=None, *args, **kwargs):
        return super(SelectPopupWidget, self).render(name, value, attrs, *args, **kwargs)

    def render(self, name, value, attrs=None, *args, **kwargs):
        return self.widget_helper.render(name, value, attrs=attrs, *args, **kwargs)

    def get_context_dict(self, base_dict, name, value, attrs, base_widget, *args, **kwargs):
        if value is None: value = ''

        model    = self.model
        opts     = self.model._meta
        instance = None
        if model and value:
            instance = model.objects.get(pk = value)

        instance_repr = u''
        if instance is not None:
            instance_repr = force_unicode(instance)

        obj_name = opts.verbose_name
        return dict(base_dict,
                    basewidget    = mark_safe(base_widget),
                    field         = mark_safe(name),
                    model         = model,
                    opts          = opts,
                    multiple      = False,
                    instance      = instance,
                    instance_repr = mark_safe(instance_repr),
                    obj_name      = mark_safe(obj_name))

class SelectMultiplePopupWidget(forms.SelectMultiple):
    """
    A widget for ManyToMany fields that allows the selection of a
    set of objects (model instances) from a QuerySet using a popup
    interface.

    This widget uses a SelectMultiple as the underlying interface,
    with an additional set of buttons.

    See the companion
    softwarefabrica.django.forms.fields.SelectMultiplePopupField form
    field.
    """

    TEMPLATE_NAME   = "forms/widgets/select-popup.html"
    TEMPLATE_LOADER = loader

    def __init__(self, model, *args, **kwargs):
        template_name   = kwargs.pop('template_name', self.TEMPLATE_NAME)
        template_loader = kwargs.pop('template_loader', self.TEMPLATE_LOADER)
        super(SelectMultiplePopupWidget, self).__init__(*args, **kwargs)
        self.template_name   = template_name
        self.template_loader = template_loader
        self.model = model
        self.widget_helper = WidgetHelper(self, *args, **kwargs)

    def render_base(self, name, value, attrs=None, *args, **kwargs):
        return super(SelectMultiplePopupWidget, self).render(name, value, attrs, *args, **kwargs)

    def render(self, name, value, attrs=None, *args, **kwargs):
        return self.widget_helper.render(name, value, attrs=attrs, *args, **kwargs)

    def get_context_dict(self, base_dict, name, value, attrs, base_widget, *args, **kwargs):
        if value is None: value = []

        model    = self.model
        opts     = self.model._meta
        #instance = []
        #if model and value:
        #    for v in value:
        #        obj = model.objects.get(pk = v)
        #        instance.append(obj)

        obj_name = opts.verbose_name
        return dict(base_dict,
                    basewidget    = mark_safe(base_widget),
                    field         = mark_safe(name),
                    model         = model,
                    opts          = opts,
                    multiple      = True,
                    instance      = None,
                    instance_repr = None,
                    obj_name      = mark_safe(obj_name))

# provide widgets with the same name as those of django.forms
Select = SelectPopupWidget
SelectMultiple = SelectMultiplePopupWidget

class SelectCascadeWidget(forms.Select):
    """
    An extended widget for ForeignKey fields that allows the selection
    of an object (model instance) from a QuerySet.
    This extension allows the cascaded update of a slave
    (ForeignKey) Select widget through AJAX.

    This widget uses a Select as the underlying interface.

    See the companion softwarefabrica.django.forms.fields.SelectCascadeField
    form field.

    The constructor requires:
      - the 'model' for the select itself;
      - the 'slave_model' for the cascaded slave select;
      - the 'slave_pivot_field', which is the field in the slave model which
        references the master 'model';
      - the 'cascade_url' for the AJAX selection/filtering view.
    """

    TEMPLATE_NAME   = "forms/widgets/select-cascade.html"
    TEMPLATE_LOADER = loader

    def __init__(self, model,
                 slave_model, slave_pivot_field,
                 attrs=None, choices=(), *args, **kwargs):
        template_name   = kwargs.pop('template_name', self.TEMPLATE_NAME)
        template_loader = kwargs.pop('template_loader', self.TEMPLATE_LOADER)
        master_selector = kwargs.pop('master_selector', None)
        slave_selector  = kwargs.pop('slave_selector', None)
        slave_widget    = kwargs.pop('slave_widget', None)
        cascade_url     = kwargs.pop('cascade_url', None)
        cascade_url     = cascade_url or reverse_lazy('forms-ajax-cascade-select')
        super(SelectCascadeWidget, self).__init__(attrs, choices, *args, **kwargs)
        self.template_name   = template_name
        self.template_loader = template_loader
        self.model             = model
        self.slave_model       = slave_model
        self.slave_pivot_field = slave_pivot_field
        self.cascade_url       = cascade_url
        self.master_selector   = master_selector
        self.slave_selector    = slave_selector
        self.slave_widget      = slave_widget
        self.widget_helper = WidgetHelper(self, *args, **kwargs)

    def render_base(self, name, value, attrs=None, *args, **kwargs):
        return super(SelectCascadeWidget, self).render(name, value, attrs, *args, **kwargs)

    def render(self, name, value, attrs=None, *args, **kwargs):
        return self.widget_helper.render(name, value, attrs=attrs, *args, **kwargs)

    def get_context_dict(self, base_dict, name, value, attrs, base_widget, *args, **kwargs):
        if value is None: value = ''
        widget_id = ''
        if attrs.has_key('id'):
            widget_id = attrs['id']
        else:
            widget_id = u'%s_id' % (name)

        slave_widget_id = ''
        if self.slave_widget:
            if self.slave_widget.attrs.has_key('id'):
                slave_widget_id = self.slave_widget.attrs['id']
            else:
                slave_widget_id = u'%s_id' % "UNKNOWN"

        model    = self.model
        opts     = self.model._meta
        instance = None
        if model and value:
            instance = model.objects.get(pk = value)

        instance_repr = u''
        if instance is not None:
            instance_repr = force_unicode(instance)

        master_selector = self.master_selector or "#%s" % widget_id
        slave_selector  = self.slave_selector or slave_widget_id

        obj_name = opts.verbose_name
        return dict(base_dict,
                    basewidget    = mark_safe(base_widget),
                    field         = mark_safe(name),
                    model         = model,
                    opts          = opts,
                    master_model  = opts.object_name,
                    master_opts   = opts,
                    master_app    = opts.app_label,
                    slave_model   = self.slave_model._meta.object_name,
                    slave_opts    = self.slave_model._meta,
                    slave_app     = self.slave_model._meta.app_label,
                    slave_pivot_field = self.slave_pivot_field,
                    cascade_url   = self.cascade_url,
                    master_selector = master_selector,
                    slave_selector  = slave_selector,
                    multiple      = False,
                    instance      = instance,
                    instance_repr = mark_safe(instance_repr),
                    obj_name      = mark_safe(obj_name))

class SelectCascadePopupWidget(SelectPopupWidget):
    """
    An extension of SelectPopupWidget that allows the cascaded
    update of a slave (ForeignKey) Select widget through AJAX.

    See the companion softwarefabrica.django.forms.fields.SelectCascadePopupField
    form field.

    The constructor requires:
      - the 'model' for the select itself;
      - the 'slave_model' for the cascaded slave select;
      - the 'slave_pivot_field', which is the field in the slave model which
        references the master 'model';
      - the 'cascade_url' for the AJAX selection/filtering view.
    """

    TEMPLATE_NAME   = "forms/widgets/select-cascade-popup.html"
    TEMPLATE_LOADER = loader

    def __init__(self, model,
                 slave_model, slave_pivot_field,
                 attrs=None, choices=(), *args, **kwargs):
        template_name   = kwargs.pop('template_name', self.TEMPLATE_NAME)
        template_loader = kwargs.pop('template_loader', self.TEMPLATE_LOADER)
        master_selector = kwargs.pop('master_selector', None)
        slave_selector  = kwargs.pop('slave_selector', None)
        slave_widget    = kwargs.pop('slave_widget', None)
        cascade_url     = kwargs.pop('cascade_url', None)
        cascade_url     = cascade_url or reverse_lazy('forms-ajax-cascade-select')
        super(SelectCascadePopupWidget, self).__init__(attrs, choices, *args, **kwargs)
        self.template_name   = template_name
        self.template_loader = template_loader
        self.model             = model
        self.slave_model       = slave_model
        self.slave_pivot_field = slave_pivot_field
        self.cascade_url       = cascade_url
        self.master_selector   = master_selector
        self.slave_selector    = slave_selector
        self.slave_widget      = slave_widget
        self.widget_helper = WidgetHelper(self, *args, **kwargs)

    def render_base(self, name, value, attrs=None, *args, **kwargs):
        return super(SelectCascadePopupWidget, self).render(name, value, attrs, *args, **kwargs)

    def render(self, name, value, attrs=None, *args, **kwargs):
        return self.widget_helper.render(name, value, attrs=attrs, *args, **kwargs)

    def get_context_dict(self, base_dict, name, value, attrs, base_widget, *args, **kwargs):
        if value is None: value = ''
        widget_id = ''
        if attrs.has_key('id'):
            widget_id = attrs['id']
        else:
            widget_id = u'%s_id' % (name)

        slave_widget_id = ''
        if self.slave_widget:
            if self.slave_widget.attrs.has_key('id'):
                slave_widget_id = self.slave_widget.attrs['id']
            else:
                slave_widget_id = u'%s_id' % "UNKNOWN"

        model    = self.model
        opts     = self.model._meta
        instance = None
        if model and value:
            instance = model.objects.get(pk = value)

        instance_repr = u''
        if instance is not None:
            instance_repr = force_unicode(instance)

        master_selector = self.master_selector or "#%s" % widget_id
        slave_selector  = self.slave_selector or slave_widget_id

        obj_name = opts.verbose_name
        return dict(base_dict,
                    basewidget    = mark_safe(base_widget),
                    field         = mark_safe(name),
                    model         = model,
                    opts          = opts,
                    master_model  = opts.object_name,
                    master_opts   = opts,
                    master_app    = opts.app_label,
                    slave_model   = self.slave_model._meta.object_name,
                    slave_opts    = self.slave_model._meta,
                    slave_app     = self.slave_model._meta.app_label,
                    slave_pivot_field = self.slave_pivot_field,
                    cascade_url   = self.cascade_url,
                    master_selector = master_selector,
                    slave_selector  = slave_selector,
                    multiple      = False,
                    instance      = instance,
                    instance_repr = mark_safe(instance_repr),
                    obj_name      = mark_safe(obj_name))
