from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.utils.html import escape, conditional_escape
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.db.models.fields.related import ManyToManyField

class ReadOnlyWidgetMixin(object):
    def __init__(self, db_field, *args, **kwargs):
        self.db_field = db_field
        super(ReadOnlyWidgetMixin, self).__init__()

    def render(self, *args, **kwargs):
        field_name, value = args
        field_type = self.db_field.__class__.__name__
        field_value = super(ReadOnlyWidgetMixin, self).render(*args, **kwargs)
        output = value

        treat_as_field_type = self.treat_as(field_type)
        if hasattr(self, 'get_%s_value' % treat_as_field_type.lower()):
            try:
                func = getattr(self, 'get_%s_value' % treat_as_field_type.lower())
                output = func(field_name, value)
            except Exception,e:
                output = e
        else:
            raise AttributeError('%s is not supported by %s.' % (field_type, type(self).__name__))

        return self.render_output(field_name, field_value, output)

    def treat_as(self, field_type):
        return field_type

    def render_output(self, field_name, field_value, output):
        return mark_safe('%s %s' % (output, field_value))

class ReadOnlyWidget(ReadOnlyWidgetMixin, forms.HiddenInput):
    def get_textfield_value(self, field_name, value):
        return '<p style="clear:both;">%s</p>' % value

    def get_charfield_value(self, field_name, value):
        if self.db_field.choices:
            for choice in self.db_field.choices:
                if value == choice[0]:
                    return conditional_escape(force_unicode(choice[1]))
        else:
            return escape(value)

    def get_integerfield_value(self, field_name, value):
        return '%d' % value

    def get_booleanfield_value(self, field_name, value):
        return _boolean_icon(value)

    def get_filefield_value(self, field_name, value):
        if value:
            return '%s <a target="_blank" href="%s">%s</a>' % (_('Currently:'), value.url, value.name)
        else:
            return ''

    def get_imagefield_value(self, field_name, value):
        return self.get_filefield_value(field_name, value)

    def get_foreignkey_value(self, field_name, value):
        try:
            obj = self.db_field.rel.to.objects.get(**{self.db_field.rel.get_related_field().name: value})
            return '<strong>%s</strong>' % unicode(obj)
        except:
            return ''

    def get_datetimefield_value(self, field_name, value):
        if value:
            return value.strftime('%x %X')
        else:
            return ''

    def get_datefield_value(self, field_name, value):
        if value:
            return value.strftime('%x')
        else:
            return ''

class ReadOnlyMultiWidget(ReadOnlyWidgetMixin, forms.MultipleHiddenInput):

    def treat_as(self, field_type):
        if isinstance(field_type, ManyToManyField) and not hasattr(self, 'get_%s_value' % field_type.lower()):
            return ManyToManyField
        else:
            return field_type

    def get_manytomanyfield_value(self, field_name, value):
        output = ['<ul class="m2m_list_%s">' % field_name,]
        for id in value:
            output.append('<li>%s</li>' % unicode(self.db_field.rel.to.objects.get(pk=id)))
        output.append('</ul>')

        return ''.join(output)
