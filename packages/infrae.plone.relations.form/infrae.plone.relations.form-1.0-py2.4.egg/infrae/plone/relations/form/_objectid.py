# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: _objectid.py 29119 2008-06-11 10:34:14Z sylvain $

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: _objectid.py 29119 2008-06-11 10:34:14Z sylvain $"

from Products.CMFCore.utils import getToolByName

from zope.interface import implements
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds

from interfaces import IPloneRelationObjectIdManager


class IntIdObjectIdManager(object):
    """Object id manager using intid."""

    implements(IPloneRelationObjectIdManager)

    def __init__(self, context):
        self.context = context
        self._intidResolver = getUtility(IIntIds, context=context.plone).register
        self._objectResolver = getUtility(IIntIds, context=context.plone).getObject

    def getObjectFromId(self, id):
        return self._objectResolver(int(id))

    def getIdFromObject(self, obj):
        return str(self._intidResolver(obj))



class ArchetypeUIDObjectIdManager(object):
    """Object id manager using archetype UID."""

    implements(IPloneRelationObjectIdManager)

    def __init__(self, context):
        self.context = context
        self.uid_catalog = getToolByName(self.context.plone, 'uid_catalog')

    def getObjectFromId(self, id):
        brains = self.uid_catalog(UID=id)
        assert len(brains) == 1
        return brains[0].getObject()

    def getIdFromObject(self, obj):
        return obj.UID()


