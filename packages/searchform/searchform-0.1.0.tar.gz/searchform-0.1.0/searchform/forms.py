# Copyright (c) 2008 by Yaco Sistemas S.L.
# Contact info: Lorenzo Gil Sanchez <lgs@yaco.es>
#
# This file is part of searchform
#
# searchform is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# searchform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with searchform.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

class SearchForm(object):
    template = 'searchform.html'
    media_template = 'media.html'

    def __init__(self, title, query_string_manager, template=None):
        self.title = title
        self.qsm = query_string_manager
        self.template = template or SearchForm.template

        self.operators_map = {}
        for field in self.fields.values():
            self.operators_map.update(dict(field.operators))

    def get_search_criteria_as_text(self):
        if self.qsm is None:
            return u''

        filters = self.qsm.get_filters()

        result = []
        for key, value in filters.items():
            field_name, operator = key.split('__')
            field = self.fields[field_name]
            result.append(field.get_query_arg_as_text(operator, value))

        separator = u' %s ' % _(u'and')
        return separator.join(result)

    def get_current_query(self):
        if self.qsm is None:
            return u''

        result = []
        filters = self.qsm.get_filters()
        for key, value in filters.items():
            field_name, operator = key.split('__')
            field = self.fields[field_name]
            query_arg = field.get_query_arg(field_name, operator, value)
            result.append(query_arg)
        separator = u' %s ' % _(u'and')
        return separator.join(result)

    def get_fields_with_query_arg_prefixes(self):
        for field_name, field in self.fields.items():
            yield field_name, field.query_arg_prefix

    def render_media(self):
        context = {
            'MEDIA_URL': settings.MEDIA_URL + 'searchform/',
            'form': self,
            }
        return render_to_string(self.media_template, context)

    def __unicode__(self):
        fields = [field.bind(field_name)
                  for field_name, field in self.fields.items()]
        context = {
            'title': self.title,
            'fields': fields,
            'query': self.get_current_query(),
            }
        return render_to_string(self.template, context)


def sanitize_filters(filters):
    """Fix filters by merging related keys

    For example, for this input:

    {'name.operator': 'contains', 'name': 'foo'}

    it produces this output:
    {'name__contains': 'foo'}
    """
    new_filters = {}
    keys_to_remove = []
    for k, v in filters.items():
        if '.' in k:
            field = k.split('.')[0]
            operator = v
            new_key = str('%s__%s' % (field, operator))
            value = filters[field]
            if value:
                new_filters[new_key] = value

            keys_to_remove.append(field)
            if field in new_filters:
                del new_filters[field]

        elif k not in keys_to_remove and v:
            new_filters[k] = v

    return new_filters
