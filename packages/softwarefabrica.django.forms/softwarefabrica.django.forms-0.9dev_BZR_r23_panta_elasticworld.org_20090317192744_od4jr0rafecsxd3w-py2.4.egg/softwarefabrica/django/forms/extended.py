# extended.py
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

from django.forms import models
from django.template import Context, RequestContext, loader

from django import forms
from django.forms.forms import BoundField

# ========================================================================
#   Extended Form support
# ------------------------------------------------------------------------

# Template-based output is based on:
#   http://code.djangoproject.com/wiki/TemplatedForm

class Form(forms.Form):
    DEFAULT_TEMPLATE = 'forms/form.html'

    def __init__(self, *args, **kwargs):
        """
        Extended Form class with support for:

            * template-based output rendering, through ``template_name``
            and ``template_loader``

        Template-based rendering is used only when ``template_name`` is specified
        and not None.

        Constructor arguments:

        ``template_name``
            name of template to use, or list of templates.

        ``template_loader``
            template loader to use (defaults to django.template.loader).

        ``enable_template``
            enable template output (defaults to True).
        """

        template_name   = kwargs.pop('template_name', self.DEFAULT_TEMPLATE)
        template_loader = kwargs.pop('template_loader', loader)
        enable_template = kwargs.pop('enable_template', True)
        super(Form, self).__init__(*args, **kwargs)
        self.template_name   = template_name
        self.template_loader = template_loader
        self.enable_template = enable_template

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

    def render_output(self, template, context_instance):
        return template.render(context_instance)

    def output_via_template(self, template_name = None, template_loader = None):
        "Helper function for rendering form via template."
        bound_fields = [BoundField(self, field, name) for name, field \
                        in self.fields.items()]
        c = Context(dict(form = self, bound_fields = bound_fields))
        t = self.get_template(template_name, template_loader)
        return self.render_output(t, c)

    def as_template(self):
        if self.template_name:
            return self.output_via_template()
        return super(Form, self).__unicode__()

    def __unicode__(self):
        if self.template_name and self.enable_template:
            return self.output_via_template()
        return super(Form, self).__unicode__()

# ========================================================================
#   Extended ModelForm support
# ------------------------------------------------------------------------

#
# Original django ModelForm structure
#
# class ModelFormMetaclass(type):
#     def __new__(cls, name, bases, attrs):
#
# class BaseModelForm(BaseForm):
#     def __init__(self, ...)
#
# class ModelForm(BaseModelForm):
#     __metaclass__ = ModelFormMetaclass

def extended_formfield_cb(field, *args, **kwargs):
    """
    formfield callback that enables new extended widgets for extended forms.

    Special (keyword) arguments:

    ``popup_models``
        a list of django db models for which popup widgets should be used

    ``not_relatedpopup``
        if True, don't use new popup widgets for ForeignKey and ManyToMany fields.

    ``old_datewidgets``
        if True, don't use new date/datetime widgets with popup calendar

    ``fallback``
        an optional formfield callback to be used as a fallback
    """
    from django.db.models.loading import get_apps, get_app, get_models, get_model
    from django.db import models
    from django.utils.text import capfirst
    from softwarefabrica.django.forms import widgets
    from softwarefabrica.django.forms import fields

    popup_models     = kwargs.pop('popup_models', None)
    not_relatedpopup = kwargs.pop('not_relatedpopup', None)
    old_datewidgets  = kwargs.pop('old_datewidgets', None)
    fallback         = kwargs.pop('fallback', None)

    required = not field.blank

    not_relatedpopup = not_relatedpopup or (popup_models == []) or (popup_models == ())

    kwargs['required'] = required

    if not not_relatedpopup:
        popup_models = popup_models or get_models()
        if isinstance(field, models.ForeignKey):
            if field.rel.to in popup_models:
                fk_model = field.rel.to
                #queryset = fk_model.objects
                queryset = field.rel.to._default_manager.complex_filter(field.rel.limit_choices_to)
                def fldconstructor(fc=fields.SelectPopupField, qs=queryset, **defaults):
                    arg_qs = defaults.pop('queryset', None)
                    return fc(qs, **defaults)
                kwargs['widget'] = widgets.SelectPopupWidget(model = fk_model)
                return field.formfield(form_class=fldconstructor, **kwargs)
                #return fields.SelectPopupField(queryset,
                #                               label=capfirst(field.verbose_name),
                #                               help_text=field.help_text,
                #                               required=required, widget = widgets.SelectPopupWidget(model = fk_model))
        elif isinstance(field, models.ManyToManyField):
            if field.rel.to in popup_models:
                fk_model = field.rel.to
                #queryset = fk_model.objects
                queryset = field.rel.to._default_manager.complex_filter(field.rel.limit_choices_to)
                def fldconstructor(fc=fields.SelectMultiplePopupField, qs=queryset, **defaults):
                    arg_qs = defaults.pop('queryset', None)
                    return fc(qs, **defaults)
                kwargs['widget'] = widgets.SelectMultiplePopupWidget(model = fk_model)
                return field.formfield(form_class=fldconstructor, **kwargs)
                #return fields.SelectMultiplePopupField(queryset, required=required, widget = widgets.SelectMultiplePopupWidget(model = fk_model))
    if isinstance(field, models.NullBooleanField):
        # this avoids Django bug #9473:
        #   http://code.djangoproject.com/ticket/9473
        kwargs['widget'] = widgets.NullBooleanSelect
        kwargs['form_class'] = fields.NullBooleanField
        return field.formfield(**kwargs)
        #return fields.NullBooleanField()
    if not old_datewidgets:
        if isinstance(field, models.DateTimeField):
            return fields.DateTimeField(*args, **kwargs)
        if isinstance(field, models.DateField):
            return fields.DateField(*args, **kwargs)

    if fallback != None:
        rv = fallback(field, *args, **kwargs)
        if rv is not None:
            return rv

    return field.formfield(*args, **kwargs)

# HACK TODO: for some reason, I need to use "ModelForm" as a base for
#            BaseModelFormFieldOrder, instead of "BaseModelForm", as
#            it would seem more natural to me.
#
#class BaseModelFormExtended(BaseModelForm):
#    def __init__(self, fieldorder = None, *args, **kwargs):
#        super(BaseModelFormExtended, self).__init__(*args, **kwargs)
#        if fieldorder:
#            self.fields.keyOrder = list(fieldorder)

class BaseModelFormExtended(models.ModelForm):
    DEFAULT_TEMPLATE = 'forms/form.html'

    def __init__(self, *args, **kwargs):
        """
        Base for an extended ModelForm which supports:

            * field order specification, through ``fieldorder`` keyword argument

            * template-based output rendering, through ``template_name``
            and ``template_loader``

        Template-based rendering is used only when ``template_name`` is specified
        and not None.

        Constructor arguments:

        ``fieldorder``
            a list of field names to be used for field ordering when rendering
            the form.

        ``template_name``
            name of template to use, or list of templates.

        ``template_loader``
            template loader to use (defaults to django.template.loader).

        ``enable_template``
            enable template output (defaults to True).
        """
        opts = self._meta
        template_name   = self.DEFAULT_TEMPLATE
        enable_template = True
        if hasattr(opts, 'template_name'):
            template_name = opts.template_name
        if hasattr(opts, 'enable_template'):
            template_name = opts.enable_template
        if ('fieldorder' not in kwargs) and hasattr(opts, 'fields') and opts.fields:
            fieldorder = list(opts.fields)
        else:
            fieldorder = kwargs.pop('fieldorder', None)
        template_name   = kwargs.pop('template_name', template_name)
        template_loader = kwargs.pop('template_loader', loader)
        enable_template = kwargs.pop('enable_template', enable_template)
        super(BaseModelFormExtended, self).__init__(*args, **kwargs)
        if fieldorder is not None:
            self.fields.keyOrder = list(fieldorder)
        self.template_name   = template_name
        self.template_loader = template_loader
        self.enable_template = enable_template

    # -- Template-based output -----------------------------------------------

    # based on:
    #   http://code.djangoproject.com/wiki/TemplatedForm

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

    def render_output(self, template, context_instance):
        return template.render(context_instance)

    def output_via_template(self, template_name = None, template_loader = None):
        "Helper function for rendering form via template."
        bound_fields = [BoundField(self, field, name) for name, field \
                        in self.fields.items()]
        c = Context(dict(form = self, bound_fields = bound_fields))
        t = self.get_template(template_name, template_loader)
        return self.render_output(t, c)

    def as_template(self):
        if self.template_name:
            return self.output_via_template()
        return super(Form, self).__unicode__()

    def __unicode__(self):
        if self.template_name and self.enable_template:
            return self.output_via_template()
        return super(BaseModelFormExtended, self).__unicode__()

class ModelFormMetaclass(models.ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        formfield_callback = attrs.pop('formfield_callback', extended_formfield_cb)
        attrs['formfield_callback'] = formfield_callback
        return super(ModelFormMetaclass, cls).__new__(cls, name, bases, attrs)

class ModelForm(BaseModelFormExtended):
    """
    A replacement for django.forms.models.ModelForm which provides our
    extensions (field ordering, ...).

    Extended widgets from softwarefabrica.django.forms.widgets are used.
    (extended widgets are enabled by using extended_formfield_cb (set in our
    verion of ModelFormMetaclass).

    See BaseModelFormExtended for constructor arguments.
    """
    __metaclass__ = ModelFormMetaclass

class ModelFormStdWidgets(BaseModelFormExtended):
    """
    A replacement for django.forms.models.ModelForm which provides our
    extensions (field ordering, ...).

    Extended widgets are *NOT* used.
    (here the standard django.forms.models.ModelFormMetaclass is used)

    See BaseModelFormExtended for constructor arguments.
    """
    __metaclass__ = models.ModelFormMetaclass

def modelform_factory(model, form=ModelForm, fields=None, exclude=None,
                      formfield_callback=extended_formfield_cb):
    """
    A replacement for django.forms.models.modelform_factory() which uses our
    extended ModelForm.
    """
    #
    # inspired by django modelform_factory()
    # see django_src/django/forms/models.py
    #
    # for dynamic ModelForm see:
    #   http://blog.handimobility.ca/tag/django/
    #   http://whynoti.org/blog/django/forms/models.py
    #
    # HACK: we should be able to construct a ModelForm without creating
    # and passing in a temporary inner class

    formfield_callback = formfield_callback or extended_formfield_cb

    class Meta:
        pass
    setattr(Meta, 'model', model)
    setattr(Meta, 'fields', fields)
    setattr(Meta, 'exclude', exclude)
    class_name = model.__name__ + 'Form'
    return ModelFormMetaclass(class_name, (form,),
                              {'Meta': Meta,
                               'formfield_callback': formfield_callback})
