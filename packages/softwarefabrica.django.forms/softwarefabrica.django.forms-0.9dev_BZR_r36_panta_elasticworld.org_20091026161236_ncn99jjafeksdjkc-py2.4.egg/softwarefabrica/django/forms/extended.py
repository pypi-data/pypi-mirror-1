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
from django.forms import Form as OriginalForm

# ========================================================================
#   Extended Form support
# ------------------------------------------------------------------------

# circumvent __all__ in django.forms
DeclarativeFieldsMetaclass = OriginalForm.__metaclass__

# Template-based output is based on:
#   http://code.djangoproject.com/wiki/TemplatedForm

class BaseForm(forms.BaseForm):
    DEFAULT_TEMPLATE = 'forms/form.html'

    def __init__(self, *args, **kwargs):
        """
        Extended (Base)Form class with support for:

            * template-based output rendering, through ``template_name``
            and ``template_loader``

        Template-based rendering is used only when ``template_name`` is specified
        and not None.

        (Extra) constructor arguments:

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
        super(BaseForm, self).__init__(*args, **kwargs)
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
        global_errors = None
        if self.is_bound:
            global_errors = self.non_field_errors()
        c = Context(dict(form = self, bound_fields = bound_fields,
                         global_errors = global_errors))
        t = self.get_template(template_name, template_loader)
        return self.render_output(t, c)

    def as_template(self):
        if self.template_name:
            return self.output_via_template()
        return super(BaseForm, self).__unicode__()

    def __unicode__(self):
        if self.template_name and self.enable_template:
            return self.output_via_template()
        return super(BaseForm, self).__unicode__()

class Form(BaseForm):
    """
    Extended Form class with support for:

        * template-based output rendering, through ``template_name``
        and ``template_loader``

    Template-based rendering is used only when ``template_name`` is specified
    and not None.

    (Extra) constructor arguments:

    ``template_name``
        name of template to use, or list of templates.

    ``template_loader``
        template loader to use (defaults to django.template.loader).

    ``enable_template``
        enable template output (defaults to True).
    """
    # This is a separate class from BaseForm in order to abstract the way
    # self.fields is specified. This class (Form) is the one that does the
    # fancy metaclass stuff purely for the semantic sugar -- it allows one
    # to define a form using declarative syntax.
    # BaseForm itself has no way of designating self.fields.
    __metaclass__ = DeclarativeFieldsMetaclass

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

class BaseModelFormSet(models.BaseModelFormSet):
    def add_fields(self, form, index):
        """Add a hidden field for the object's primary key."""
        from django.db.models import AutoField
        from django.forms.fields import CharField
        from django.forms.widgets import HiddenInput
        pk = self.model._meta.pk
        self._pk_field = pk
        if pk.auto and (pk.name == 'uuid'):
            instance = None
            if (index < self._initial_form_count):
                instance = self.get_queryset()[index]
            if instance:
                form.fields[pk.name] = CharField(required=False, max_length=pk.max_length, initial=instance.pk, widget=HiddenInput)
            else:
                form.fields[pk.name] = CharField(required=False, max_length=pk.max_length, widget=HiddenInput)
        super(BaseModelFormSet, self).add_fields(form, index)

def modelformset_factory(model, form=ModelForm,
                         formfield_callback=extended_formfield_cb,
                         formset=BaseModelFormSet,
                         extra=1, can_delete=False, can_order=False,
                         max_num=0, fields=None, exclude=None):
    """
    A replacement for django.forms.models.modelformset_factory() which uses
    our extended ModelForm.

    Returns a FormSet class for the given Django model class.
    """
    from django.forms.formsets import formset_factory

    form = modelform_factory(model, form=form, fields=fields, exclude=exclude,
                             formfield_callback=formfield_callback)
    FormSet = formset_factory(form, formset, extra=extra, max_num=max_num,
                              can_order=can_order, can_delete=can_delete)
    FormSet.model = model
    return FormSet

# ========================================================================
#   FormBuilder
# ------------------------------------------------------------------------

class FormBuilder(object):
    """
    Dynamically builds a form class / form.

    >>> fb = FormBuilder('TestForm', MediaContent)
    >>> fb.add_field('name', validator=lambda self: self.cleaned_data['name'].lower())
    >>> fb.add_field('title', required=False)
    >>> fb.add_field('slug', required=False)
    >>> fb.add_field('date', required=False, name_in_model='m_date')
    >>> fb.add_field('quality', required=False, reference_model=MediaSize)
    >>> formC = fb.get_form_class()
    """

    class FormBuilderField(object):
        def __init__(self, fb, name, label=None,
                     required=None,
                     help_text=None,
                     error_messages=None,
                     initial=None,
                     include_blank=None,
                     null=None,
                     field=None, widget=None,
                     widget_args=None, widget_kwargs=None,
                     validator=None,
                     reference_model=None,
                     name_in_model=None,
                     **field_kwargs):
            assert isinstance(fb, FormBuilder)
            self.fb             = fb
            self.name           = name
            self.label          = label
            self.required       = required
            self.help_text      = help_text
            self.error_messages = error_messages
            self.initial        = initial
            self.include_blank  = include_blank
            self.null           = null
            self.field          = field
            self.widget         = widget
            self.widget_args    = widget_args or ()
            self.widget_kwargs  = widget_kwargs or {}
            self.validator      = validator
            self.reference_model = reference_model
            self.name_in_model  = name_in_model
            self.field_kwargs   = field_kwargs or {}

            self._db_field      = None
            self._db_model      = None

            self._setup()

        def _setup(self):
            from django.db.models.fields import Field
            from django.db.models.fields import FieldDoesNotExist
            from django.utils.text import capfirst

            if self.reference_model:
                self._db_model = self.reference_model
            elif self.fb.reference_model:
                self._db_model = self.fb.reference_model
            
            if self._db_model:
                opts = self._db_model._meta
                if not self._db_field:
                    try:
                        self._db_field = opts.get_field(self.model_field_name)
                    except FieldDoesNotExist:
                        pass

            if self._db_field:
                assert isinstance(self._db_field, Field)
                self.label = self.label or capfirst(self._db_field.verbose_name)
                if ('max_length' in self.field_kwargs) and (self.field_kwargs['max_length'] == -1):
                    self.field_kwargs['max_length'] = self._db_field.max_length
                if self.required is None:
                    self.required = not self._db_field.blank
                self.help_text = self.help_text or self._db_field.help_text
                self.initial = self.initial or self._db_field.get_default()
                if (not self.field) or isinstance(self.field, type):
                    field_kwargs = dict(label      = self.label,
                                        required   = self.required,
                                        help_text  = self.help_text,
                                        initial    = self.initial)
                    field_kwargs.update(self.field_kwargs)
                    if self._db_field.choices:
                        if self.null is not None:
                            if self.null and 'empty_value' not in field_kwargs:
                                field_kwargs['empty_value'] = None
                        if (self.include_blank is not None) and ('choices' not in field_kwargs):
                            field_kwargs['choices'] = self._db_field.get_choices(include_blank=self.include_blank)
                    if self.widget:
                        if isinstance(widget, type):
                            widget = widget(*self.widget_args, **self.widget_kwargs)
                        field_kwargs['widget'] = widget
                    if not self.field:
                        self.field = self._db_field.formfield(**field_kwargs)
                    elif isinstance(self.field, type):
                        self.field = self.field(**field_kwargs)
            return self

        @property
        def model_field_name(self):
            if self.name_in_model:
                return self.name_in_model
            return self.name

    def __init__(self, name, reference_model=None,
                 validator=None,
                 base_form_class=None,
                 fields=None):
        """
        ``reference_model`` is an optional Model that will be used as a reference
        to retrieve fields meta information if not provided explicitly (for
        example, labels, help text, ...).
        """
        self.name            = name
        self.reference_model = reference_model
        self.validator       = validator
        self.base_form_class = base_form_class

        self.fb_fields       = {}
        self.fb_fields_list  = []

        if fields:
            self._add_fields(fields)

    def add_field(self, name, label=None, required=None,
                  help_text=None,
                  error_messages=None,
                  initial=None,
                  field=None, widget=None,
                  widget_args=None, widget_kwargs=None,
                  validator=None,
                  reference_model=None,
                  name_in_model=None,
                  **field_kwargs):
        fb_field = FormBuilder.FormBuilderField(self, name,
                                                label = label,
                                                required = required, help_text = help_text,
                                                error_messages = error_messages,
                                                initial = initial,
                                                field = field, widget = widget,
                                                widget_args = widget_args,
                                                widget_kwargs = widget_kwargs,
                                                validator = validator,
                                                reference_model = reference_model,
                                                name_in_model = name_in_model,
                                                **field_kwargs)
        if name not in self.fb_fields:
            self.fb_fields[name] = fb_field
            self.fb_fields_list.append(fb_field)
        return fb_field

    def get_form_class(self):
        """
        Return the form class for this form.
        """

        #from django.forms import BaseForm
        from softwarefabrica.django.forms.extended import BaseForm

        base_fields = self._get_base_fields()
        base_form_class = self.base_form_class or BaseForm
        new_class = type(self.name, (base_form_class,),
                         { 'base_fields': base_fields, })

        # add validation methods
        for fb_field in self.fb_fields_list:
            assert isinstance(fb_field, FormBuilder.FormBuilderField)
            if fb_field.validator:
                method_name = 'clean_%s' % fb_field.name
                setattr(new_class, method_name, fb_field.validator)

        if self.validator:
            setattr(new_class, 'clean', self.validator)

        return new_class

    form_class = property(get_form_class, None, None, "The form class")

    def form(self, *form_args, **form_kwargs):
        formClass = self.get_form_class()
        return formClass(*form_args, **form_kwargs)

    def _get_base_fields(self):
        from django.utils.datastructures import SortedDict
        base_fields = []
        for fb_field in self.fb_fields_list:
            assert isinstance(fb_field, FormBuilder.FormBuilderField)
            base_fields.append((fb_field.name, fb_field.field))
        return SortedDict(base_fields)

    def _add_fields(self, fields):
        for field in fields:
            if isinstance(field, dict):
                name = field['name']
                f_kwargs = {}
                f_kwargs.update(field)
                del f_kwargs['name']
                self.add_field(name, f_kwargs)
            else:
                assert isinstance(field, basestring)
                self.add_field(field)
        return self
