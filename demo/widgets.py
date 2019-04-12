# -*- coding: utf-8 -*-
from django.utils.dates import MONTHS
from django.forms.widgets import Widget, Select
import re
import datetime
from DateTime.DateTime import basestring
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.forms import widgets
from django.conf import settings
from leaflet.templatetags.leaflet_tags import leaflet_map
from django.utils.translation import gettext_lazy as _


class RelatedFieldWidgetCanAdd(widgets.Select):

    def __init__(self, related_model, related_url=None, *args, **kw):

        super(RelatedFieldWidgetCanAdd, self).__init__(*args, **kw)

        if not related_url:
            rel_to = related_model
            info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
            related_url = 'admin:%s_%s_add' % info

        # Be careful that here "reverse" is not allowed
        self.related_url = related_url

    def render(self, name, value, renderer=None, *args, **kwargs):
        self.related_url = reverse(self.related_url)
        output = [super(RelatedFieldWidgetCanAdd, self).render(name, value, renderer=None, *args, **kwargs)]
        output.append(u'<a data-toggle="modal" href="#" data-form="%s" class="add-related" id="add_id_%s" >modal</a>&nbsp;' %
                      (self.related_url, name))
        output.append(u'<a href="%s" class="add-related_plain" id="add_myid_%s" >add</a>' %
                      (self.related_url, name))
        #output.append(u'<img src="%sadmin/img/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.STATIC_URL, 'Add'))
        return mark_safe(u''.join(output))


class CustomBootrapTextInputWidget(widgets.TextInput):

    # def __init__(self, related_model, related_url=None, *args, **kw):
    #
    #     super(CustomBootrapTextInputWidget, self).__init__(*args, **kw)
    #
    #     if not related_url:
    #         rel_to = related_model
    #         info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
    #         related_url = 'admin:%s_%s_add' % info
    #
    #     # Be careful that here "reverse" is not allowed
    #     self.related_url = related_url

    def render(self, name, value, renderer=None, *args, **kwargs):
        #self.related_url = reverse(self.related_url)
        output = [super(CustomBootrapTextInputWidget, self).render(name, value, renderer=None, *args, **kwargs)]
        # output.append(u'<a data-toggle="modal" href="#" data-form="%s" class="add-related" id="add_id_%s" >modal</a>&nbsp;' % \
        #    (self.related_url, name))
        # output.append(u'<a href="%s" class="add-related_plain" id="add_myid_%s" >add</a>' % \
        #    (self.related_url, name))
        #output.append(u'<img src="%sadmin/img/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.STATIC_URL, 'Add'))
        return mark_safe(u''.join(output))


class LeafletMapWidget(widgets.TextInput):

    def __init__(self, tag_id, *args, **kw):

        super(LeafletMapWidget, self).__init__(*args, **kw)

        if not tag_id:
            tag_id = 'lf_map'

        # Be careful that here "reverse" is not allowed
        self.tag_id = tag_id

    def render(self, name, value, *args, **kwargs):
        output = [super(LeafletMapWidget, self).render(
            name, value, *args, **kwargs)]
        output.append(u"<div id='{}' ></div>".format(self.tag_id))
        return mark_safe(u''.join(output))


__all__ = ('MonthYearWidget',)

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')


class MonthYearWidget(Widget):
    """
    A Widget that splits date input into two <select> boxes for month and year,
    with 'day' defaulting to the first of the month.

    Based on SelectDateWidget, in

    django/trunk/django/forms/extras/widgets.py


    """
    #none_value = (0, 'Wählen ...')
    #month_none_value = (0, _('Select month ...'))
    # year_none_value = ('', _('Select year ...'))
    month_field = '%s_month'
    year_field = '%s_year'

    def __init__(self, attrs=None, years=None, required=True):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        self.required = required
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year - 4, this_year + 2)

    def render(self, name, value, attrs=None, renderer=None):
        try:
            year_val, month_val = value.year, value.month
        except AttributeError:
            year_val = month_val = None
            if isinstance(value, basestring):
                match = RE_DATE.match(value)
                if match:
                    year_val, month_val, day_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        month_choices = MONTHS.items()
        # if not (self.required and value):
        #MONTHS[0] = self.month_none_value[1]
        # month_choices.append(self.none_value)
        #month_choices = MONTHS.items()
        month_choices = sorted(month_choices)
        #myfield = self.month_field % id_
        # , extra_attrs={id: myfield}
        local_attrs = self.build_attrs(base_attrs={})
        local_attrs['id'] = self.month_field % id_
        s = Select(choices=month_choices)
        select_html = s.render(self.month_field % name, month_val, local_attrs)
        output.append(select_html)

        year_choices = [(i, i) for i in self.years]
        # if not (self.required and value):
        #     year_choices.insert(0, self.year_none_value)
        local_attrs['id'] = self.year_field % id_
        s = Select(choices=year_choices)
        select_html = s.render(self.year_field % name, year_val, local_attrs)
        output.append(select_html)

        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_

    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        if y == m == "0":
            return None
        if y and m:
            return '%s-%s-%s' % (y, m, 1)
        return data.get(name, None)
