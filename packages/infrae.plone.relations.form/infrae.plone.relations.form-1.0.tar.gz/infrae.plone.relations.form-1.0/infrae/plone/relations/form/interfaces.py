# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: interfaces.py 29119 2008-06-11 10:34:14Z sylvain $

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: interfaces.py 29119 2008-06-11 10:34:14Z sylvain $"

from zope.app.form.interfaces import IInputWidget, IDisplayWidget
from zope.interface import Interface, Attribute
from zope.i18nmessageid import MessageFactory

_ = MessageFactory("plone")


class IPloneRelationDisplayWidget(IDisplayWidget):
    """A widget to display plone relation.
    """

class IPloneRelationObjectIdManager(Interface):
    """Manage object's id.
    """

    def getObjectFromId(id):
        """With the given id, return object.
        """

    def getIdFromObject(self, obj):
        """With the object, return object.
        """
        

class IPloneRelationEditWidget(IInputWidget):
    """A widget to edit plone relation.
    """

    plone = Attribute(_(u"Plone site context"))
    field = Attribute(_(u"Field being rendered"))

    
class IPloneRelationEditWidgetView(Interface):
    """Helper view for edit widget.
    """

    plone = Attribute(_(u"Plone site context."))
    add_widget = Attribute(_(u"Widget used to add new values"))
    add_widget_args = Attribute(_(u"Options for add widget"))
    edit_context = Attribute(_(u"Widget to edit context"))

    def getName():
        """Return the name of the widget.
        """

    def getPloneContext():
        """Like plone property, but for page template as you can't
           acces property in a Zope 2 page template...
        """

    def getRelationCount():
        """Return the number of relation in the widget.
        """

    def getRelationToRender():
        """Return the relation data to render.
        """

    def canAddValues():
        """Return true if the user is allowed to add new values.
        """

    def hasValue(value):
        """Check if value is already in the relation.
        """

    def relationIsUnique():
        """Return true if the relation must contains simple items.
        """

    def relationUseContext():
        """Return true if the relation use context items.
        """

    def relationAsOneItem():
        """Return true if the relation as only one item for the
           moment.
        """

    def renderEditContext():
        """Render a box to edit context of a relation.
        """

    def renderAddWidget():
        """Render the add widget.
        """


class IPloneRelationSubWidget(Interface):
    """Base interface for plone relation sub widget.
    """

    def hasInput():
        """Return true if the widget have input (after being called).
        """

    def getInputValue():
        """Return input value.
        """


class IPloneRelationEditContext(IPloneRelationSubWidget):
    """Subwidget to edit context on a relation.
    """

    context_schema = Attribute(_(u"Schema of the object"))
    context_factory = Attribute(_(u"Factory for new context object"))

    def setPrefix(uid):
        """Set a prefix for field (to prevent collision).
        """

    def setRenderedValue(obj):
        """Set the object to render.
        """

    def applyChanges(obj):
        """Apply changes on given object.
        """

    def error():
        """Return the error on the widget.
        """

class IPloneRelationAddWidget(IPloneRelationSubWidget):
    """Subwidget to add new relation. This is build using a
       IPloneRelationEditWidgetView as context.
    """





