# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: _view.py 29160 2008-06-12 12:17:45Z sylvain $

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: _view.py 29160 2008-06-12 12:17:45Z sylvain $"


from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.interface import implements
from zope.component import getMultiAdapter

from zope.app.form.browser.widget import renderElement

from Acquisition import Explicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass as initializeClass

from interfaces import IPloneRelationEditWidgetView, IPloneRelationEditContext
from _context import PloneRelationEditContext


from sets import Set
import operator


class PloneRelationDisplayView(Explicit):
    """View class to display plone relation items"""

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    template = ViewPageTemplateFile('plonerelation_view.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        # Translation don't work in this template under Plone 3 ...
        return self.template()

    def getRelationToRender(self):
        items = []
        for value in self.context.cached_values:
            data = dict()
            objs = []
            for obj in value['objects']:
                data_obj = dict(title=obj.Title(),
                                url=obj.absolute_url())
                objs.append(data_obj)
            data['objects'] = objs
            if self.context.relationUseContext():
                context = value['context']
                data['context'] = dict(title=context.Title(),
                                       url=context.absolute_url())
            items.append(data)

        return items

initializeClass(PloneRelationDisplayView)



class PloneRelationEditView(Explicit):
    """This view is used to render the template of the plone relation
    widget using a valid context.

    It also contains a bunch of methods to get data for this template.
    """

    implements(IPloneRelationEditWidgetView)

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    template = ViewPageTemplateFile('plonerelation_edit.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._add_widget = None
        self._add_widget_args = None
        self._cached_ids = None
        self._cached_values = None

        self._edit_context = getMultiAdapter((self, request), IPloneRelationEditContext)

    def _prepareData(self):
        items = []
        ids = []
        count = 0
        for value in self.context.cached_values:
            data = dict(nb=count,
                        modify=False)
            objs = []
            for obj in value['objects']:
                obj_id = self.context.getIdForObject(obj)
                data_obj = dict(title=obj.Title(),
                                uid=obj_id,
                                url=obj.absolute_url())
                objs.append(data_obj)
                ids.append(obj_id)
            data['objects'] = objs
            if self.relationUseContext():
                context_id = self.context.getIdForObject(value['context'])
                data['context'] = context_id
                if context_id == self.context.edited_context:
                    data['modify'] = True
            items.append(data)
            count += 1

        self._cached_values = items
        self._cached_ids = Set(ids)

    def __call__(self):
        self._prepareData()
        return self.template()

    def _refresh_add_args(self):
        for k, v in self._add_widget_args.iteritems():
            setattr(self._add_widget, k, v)

    @apply
    def add_widget():
        def get(self):
            return self._add_widget
        def set(self, value):
            self._add_widget = value(self, self.request)
            if self._add_widget_args:
                self._refresh_add_args()
        return property(get, set)

    @apply
    def add_widget_args():
        def get(self):
            return self._add_widget_args
        def set(self, value):
            assert isinstance(value, dict)
            self._add_widget_args = value
            if self._add_widget:
                self._refresh_add_args()
        return property(get, set)

    @property
    def edit_context(self):
        return self._edit_context

    def getRelationCount(self):
        return len(self.context.cached_values)

    def getRelationToRender(self):
        return self._cached_values

    def hasValue(self, value):
        return value in self._cached_ids

    def relationIsUnique(self):
        return self.context.field.unique

    def relationUseContext(self):
        return self.context.relationUseContext()

    def relationAsOneItem(self):
        return self.getRelationCount() == 1

    def getPloneContext(self):
        return self.plone

    def getName(self):
        return self.context.name

    def canAddValues(self):
        maxl = self.context.field.max_length
        return self.add_widget and not self.context.edited_context and ((not maxl) or (len(self.context.cached_values) < maxl))

    @property
    def plone(self):
        return self.context.plone

    def renderAddWidget(self):
        return self._add_widget()

    def renderEditContext(self):
        all = self._edit_context()
        if self.context.edited_context:
            all += renderElement('input',
                                 type='hidden',
                                 value=self.context.edited_context,
                                 name='%s.modify_uid' % self.getName())
            
        return all

    def nameToId(self, string):
        return string.replace('.', '-')


initializeClass(PloneRelationEditView)

