# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: _widget.py 29160 2008-06-12 12:17:45Z sylvain $

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: _widget.py 29160 2008-06-12 12:17:45Z sylvain $"

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.interface import implements
from zope.app.form.browser.widget import SimpleInputWidget, DisplayWidget
from zope.app.form.interfaces import WidgetsError, MissingInputError
from plone.relations.lazylist import lazyresolver

from Acquisition import Explicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass as initializeClass

from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("plone")

from interfaces import *

from _view import PloneRelationEditView, PloneRelationDisplayView

def _object_property(name):
    """Export property on render sub-object.
    """
    def get(self):
        return getattr(self.render, name)
    def set(self, value):
        return setattr(self.render, name, value)
    return property(get, set)


class PloneRelationMixin(object):
    """Mixin of usefull methods.
    """

    @property
    def plone(self):
        return self.context.context

    @property
    def field(self):
        return self.context

    def relationUseContext(self):
        return not (self.field.context_schema is None)

    

class PloneRelationEditWidget(Explicit, SimpleInputWidget, PloneRelationMixin):
    """Widget to edit plone relation.
    """

    implements(IPloneRelationEditWidget)

    security = ClassSecurityInfo()

    def __init__(self, context, request):
        super(PloneRelationEditWidget, self).__init__(context, request)

        self.cached_values = []
        self.render = PloneRelationEditView(self, self.request)
        self.object_manager = IPloneRelationObjectIdManager(self)
        self.edit_context.context_schema = self.field.context_schema
        self.edited_context = None


    add_widget = _object_property('add_widget')
    add_widget_args = _object_property('add_widget_args')
    edit_context = _object_property('edit_context')

    def __call__(self):
        """Render method.
        """
        self.cached_values = self._getRenderedValue()
        return self.render()


    def hasInput(self):
        """ Return true if the form has input data.
        """
        return ('%s.marker' % self.name) in self.request.form

    def setPrefix(self, prefix):
        super(PloneRelationEditWidget, self).setPrefix(prefix)
        self.edit_context.setPrefix()

    def getIdForObject(self, obj):
        """Convienence method.
        """
        return self.object_manager.getIdFromObject(obj)

    def _relationResolver(self, data_ids):
        oids, context_id = data_ids
        objs = []
        for oid in oids:
            objs.append(self.object_manager.getObjectFromId(oid))
        data = dict(objects=objs)
        if context_id:
            data['context'] = self.object_manager.getObjectFromId(context_id)
        return data
    

    def _contextModification(self, i, modified_context_id):
        """Check for modification on context.
        """
        context_id = self.request.form.get("%s.context_%d" % (self.name, i))
        modification = ("%s.modify_%d" % (self.name, i)) in self.request.form
        if modification:                # Ask for a modification.
            context_obj = self.object_manager.getObjectFromId(context_id)
            self.edit_context.setRenderedValue(context_obj)
            self.edited_context = context_id
        elif context_id == modified_context_id: # Save a modification.
            self.edit_context.setPrefix(context_id)
            if self.edit_context.hasInput():
                context_obj = self.object_manager.getObjectFromId(context_id)
                try:
                    self.edit_context.applyChanges(context_obj)
                except Exception, e:    # There is erros, reask a modification.
                    self.edit_context.setRenderedValue(context_obj)
                    self.edited_context = context_id
                else:
                    self.edit_context.setPrefix() # Reset the widget for a new use.
        return context_id


    def _contextAdd(self, target_id):
        """Create a new context after adding a element.
        """
        target_obj = self.object_manager.getObjectFromId(target_id)
        self.edit_context.setPrefix()
        data = self.edit_context.getInputValue()
        context_obj = self.context_factory(self.context.context, target_obj, data)
        return self.object_manager.getIdFromObject(context_obj)


    @lazyresolver(resolver_name="_relationResolver")
    def _generateRelations(self):
        """Get the relations items from the form.
        """
        try:
            count = int(self.request.form.get(self.name + ".marker"))
        except KeyError:
            raise WidgetInputError(self.context.__name__, self.context.title)

        relations = [None] * count
        modified_context_id = self.request.form.get("%s.modify_uid" % self.name, None)
        for i in reversed(range(count)):
            removing = ("%s.remove_%d" % (self.name, i)) in self.request.form
            if removing:
                del relations[i]
            else:
                context_id = None
                if self.relationUseContext():
                   context_id = self._contextModification(i, modified_context_id)

                relations[i] = (self.request.form["%s.%d" % (self.name, i)], context_id,)

        if self.add_widget and self.add_widget.hasInput():
            target_ids = self.add_widget.getInputValue()
            context_id = None
            assert target_ids
            if self.relationUseContext():
                context_id = self._contextAdd(target_ids[0])
            relations.append((target_ids, context_id,))

        return relations

  
    def _valuesToForm(self, data):
        """Convert field value to form value.
        """
        return data

    def _formToValues(self, data):
        """Convert form value to field value.
        """
        return data

    def _getRenderedValue(self):
        """Returns relations from the request or _data.
        """
        if self._renderedValueSet():
            relations = self._valuesToForm(self._data)
        elif self.hasInput():
            relations = self._generateRelations()
        elif self.context.default is not None:
            relations = self._valuesToForm(self.context.default)
        else:
            relations = []
        return relations


    def getInputValue(self):
        """Return the input value of the widget.
        """
        if self.hasInput():
            self.preserve_widgets = True
            relations = self._formToValues(self._generateRelations())
            if not relations and self.context.required:
                raise MissingInputError(self.context.__name__,
                                        self.context.title)
            return relations
        raise MissingInputError(self.context.__name__, self.context.title)


    def hidden(self):
        """Hidden widget.
        """
        return ""

initializeClass(PloneRelationEditWidget)



class PloneRelationDisplayWidget(Explicit, DisplayWidget, PloneRelationMixin):
    """Display a plone relation item.
    """

    implements(IPloneRelationDisplayWidget)

    security =  ClassSecurityInfo()

    def __init__(self, context, request):
        super(PloneRelationDisplayWidget, self).__init__(context, request)
        self.render = PloneRelationDisplayView(self, request)

    def __call__(self):
        self.cached_values = self._data
        return self.render()


initializeClass(PloneRelationDisplayWidget)

