# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: _context.py 29200 2008-06-13 09:56:46Z sylvain $

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: _context.py 29200 2008-06-13 09:56:46Z sylvain $"

from zope.interface import implements
from zope.schema import getFieldNamesInOrder
from zope.component import getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser.interfaces import IWidgetInputErrorView
from zope.app.form.utility import setUpWidgets, setUpEditWidgets

from Acquisition import Explicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass as initializeClass

from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("plone")

from interfaces import IPloneRelationEditContext


class PloneRelationEditContext(Explicit):

    implements(IPloneRelationEditContext)

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    template = ViewPageTemplateFile('editcontext.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self._rendered = False
        self._context_schema = None
        self._context_names = None
        self._context_factory = None
        self._errors = dict()


    def __call__(self):
        assert self.context_schema
        return self.template()


    @apply
    def context_schema():
        def get(self):
            return self._context_schema
        def set(self, value):
            if value:
                self._context_schema = value
                self._context_names = getFieldNamesInOrder(value)
                self.setPrefix()
        return property(get, set)

    @apply
    def context_factory():
        def get(self):
            return self._context_factory
        def set(self, value):
            self._context_factory = value
        return property(get, set)

    
    def applyChanges(self, obj):
        """Apply changes on given obj.
        """
        value = self.getInputValue()
        for name in self._context_names:
            field = self._context_schema.get(name)
            field.set(obj, value[name])

    def setPrefix(self, uid=None, noset=False):
        prefix = '%s.edit_context' % self.context.getName()
        rendered = False
        if uid:
            prefix = '%s.%s' % (prefix, uid)
            rendered = True
        self._context_prefix = prefix
        self._rendered = rendered
        if not noset and self._context_schema:
            setUpWidgets(self, self._context_schema, IInputWidget,
                         prefix=self._context_prefix,
                         names=self._context_names,
                         context=self.context.plone)


    def getContextWidget(self, name):
        """Return the widget named name.
        """
        return getattr(self, '%s_widget' % name)

    def getContextWidgets(self):
        """Return all widgets.
        """
        return [self.getContextWidget(name) for name in self._context_names]

    def hasButton(self):
        return self._rendered

    def setRenderedValue(self, obj):
        """Set the object to render.
        """
        self.setPrefix(self.context.context.getIdForObject(obj), noset=True)
        setUpEditWidgets(self, self._context_schema, obj,
                         prefix=self._context_prefix,
                         names=self._context_names,
                         context=self.context.plone)


    def hasInput(self):
        """Return true if the widget have input (after being called).
        """
        if self._rendered:
            button = '%s.modify_apply' % self.context.getName()
            if not button in self.request.form:
                return False
        for name in self._context_names:
            if self.getContextWidget(name).hasInput():
                return True
        return False

    def getInputValue(self):
        """Return a dict with form content.
        """
        data = dict()
        error = None 
        for name in self._context_names:
            try:
                data[name] = self.getContextWidget(name).getInputValue()
            except Exception, e:
                if not error:
                    error = e
                self._errors[name] = e
        if error:
            raise error
        return data

    def error(self):
        """Return the error on the widget.
        """
        if self._errors:
            errormessages = []
            keys = self._errors.keys(); keys.sort()
            for key in keys:
                errormessages.append(str(key) + ': ')
                errormessages.append(getMultiAdapter((self._errors[key], self.request),
                                                     IWidgetInputErrorView).snippet())
            return ''.join(errormessages)
        return ""


    def nameToId(self, string):
        return string.replace('.', '-')


initializeClass(PloneRelationEditContext)


