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

import copy

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

class BaseSearchTerm(object):
    template = 'base_search_term.html'
    operators = tuple()

    def __init__(self, label, menuitem_label, query_arg_prefix, template=None):
        self.label = label
        self.menuitem_label = menuitem_label
        self.query_arg_prefix = query_arg_prefix
        self.operators_map = dict(self.operators)
        self.field_name = None
        self.template = template or self.__class__.template

    def is_binded(self):
        return not (self.field_name is None)

    def bind(self, field_name):
        clone = copy.copy(self)
        clone.field_name = field_name
        return clone

    def get_query_arg_as_text(self, operator, value):
        operator_label = self.operators_map[operator]
        return u'%s %s %s' % (self.query_arg_prefix, operator_label, value)

    def get_query_arg(self, field_name, operator, value):
        common_string = u"%s-%s-query-arg" % (field_name, operator)
        result = [u'<span class="query-arg">%s ' % self.query_arg_prefix]
        result.append(u'<a id="%s" name="%s" href="%s">'
                      % (common_string, operator, field_name))
        operator_label = self.operators_map[operator]
        result.append(u'%s <span>%s</span>' % (operator_label, value))
        result.append(u'</a>')
        result.append(u'<button class="remove-action" attr="%s" name="%s">%s</button>' %
                      (field_name, common_string, _(u'remove')))
        result.append(u'</span>')
        return u''.join(result)

    def render_searchlet_block(self):
        options = [{'operator': op, 'label': label}
                   for op, label in self.operators]
        context = {
            'field': self,
            'options': options,
            }
        return render_to_string(self.template, context)


class SphinxSearchTerm(BaseSearchTerm):
    operators = (
        ('icontains', _('contains')),
        )


class TextSearchTerm(BaseSearchTerm):
    operators = (
        ('icontains', _('contains')),
        ('not_contains', _('does not contains')),
        ('istartswith', _('starts with')),
        ('exact', _('is exactly')),
        )


class LongTextSearchTerm(TextSearchTerm):
    template = 'long_text_search_term.html'


class DateSearchTerm(BaseSearchTerm):
    operators = (
        ('exact', _('is exactly')),
        ('gt', _('greater than')),
        ('lt', _('less than')),
        ('period', _('period')),
        ('century', _('century')),
        )


class ExclusiveOptionsSearchTerm(BaseSearchTerm):
    options = ()
    template = 'exclusive_options_search_term.html'
    operators = ()
    operator = ''
    operator_label = ''


class MultipleOptionsSearchTerm(BaseSearchTerm):

    select_size = 7
    options = ()
    model = None
    operators = (
        ('in', ''),
        )
    operator = operators[0][0]
    operator_label = operators[0][1]
    template = 'multiple_options_search_term.html'

    def render_searchlet_block(self):
        options = [{'operator': op, 'label': label}
                   for op, label in self.options]
        context = {
            'field': self,
            'options': options,
            }
        return render_to_string(self.template, context)


class ObjectsSearchTerm(MultipleOptionsSearchTerm):

    model = None

    def _options(self):
        queryset = self.model.objects.all()
        return [(obj.id, unicode(obj)) for obj in queryset]

    options = property(_options)

    def _get_value_text(self, value):
        value_text = []
        for obj_id in value:
            obj = self.model.objects.get(id=int(obj_id))
            value_text.append(unicode(obj))
        return u', '.join(value_text)

    def get_query_arg_as_text(self, operator, value):
        value_text = self._get_value_text(value)
        operator_label = self.operators_map[operator]
        return u'%s %s %s' % (self.query_arg_prefix, operator_label, value_text)

    def get_query_arg(self, field_name, operator, value):
        value_text = self._get_value_text(value)
        return super(ObjectsSearchTerm, self).get_query_arg(field_name,
                                                            operator,
                                                            value_text)
