# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: _add.py 29160 2008-06-12 12:17:45Z sylvain $

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: _add.py 29160 2008-06-12 12:17:45Z sylvain $"

from zope.interface import implements
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyTokenized
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Acquisition import Explicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass as initializeClass

from interfaces import IPloneRelationAddWidget


class BaseAddWidget(Explicit):
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """Render the widget.
        """
        return self.template()


    def hasInput(self):
        """Return true if the widget have input (after being called).
        """
        name = '%s.add_button' % self.context.getName()
        return (name in self.request.form)

    def getInputValue(self):
        """Return a list of object UID for the new relation.
        """
        return self.request.form["%s.add_value" % self.context.getName()]

    def getButtonType(self):
        if self.context.relationIsUnique():
            return 'radio'
        return 'checkbox'

    def nameToId(self, string):
        #  '.' is special in CSS, so replace to '-'
        return string.replace('.', '-')


class BaseSearchAddWidget(BaseAddWidget):

    content_type = None
    review_state = None

    def getInputValue(self):
        """Return a list of object UID for the new relation.
        """
        return self.request.form["%s.add_value" % self.context.getName()]


    def getSearchResult(self):
        assert self.content_type
        catalog = getToolByName(self.context.plone, 'portal_catalog')
        criteria = dict(portal_type=self.content_type)
            
        search_value = self.getSearchValue()
        if search_value:
            criteria['Title'] = '%s*' % search_value
        if self.review_state:
            criteria['review_state'] = self.review_state

        result = []
        for brain in catalog(**criteria):
            obj = brain.getObject()
            uid = self.context.context.getIdForObject(obj)
            if not self.context.hasValue(uid):
                data = dict(title=obj.Title(),
                            url=obj.absolute_url(),
                            uid=uid)
                result.append(data)
        return result


class PloneRelationListAddWidget(BaseSearchAddWidget):
    """Add widget using a listing.
    """

    implements(IPloneRelationAddWidget)

    security = ClassSecurityInfo()
    security.declareObjectPublic()
    template = ViewPageTemplateFile('addrelation_list.pt')

    def getSearchValue(self):
        return None

    
initializeClass(PloneRelationListAddWidget)


class PloneRelationSearchAddWidget(BaseSearchAddWidget):
    """Add widget using a search.
    """

    implements(IPloneRelationAddWidget)

    security = ClassSecurityInfo()
    security.declareObjectPublic()
    template = ViewPageTemplateFile('addrelation_search.pt')


    def hasAskForInput(self):
        """Return true if the widget have been called.
        """
        name = '%s.search_button' % self.context.getName()
        return (name in self.request.form)

    def getSearchValue(self):
        name = '%s.search_value' % self.context.getName()
        if name in self.request.form:
            return self.request.form[name]
        return ""

    def getSearchResult(self):
        if self.hasAskForInput():
            return super(PloneRelationSearchAddWidget, self).getSearchResult()
        return []

initializeClass(PloneRelationSearchAddWidget)


class PloneRelationVocabularyAddWidget(BaseAddWidget):
    """Add widget using a vocabulary.
    """

    implements(IPloneRelationAddWidget)

    security = ClassSecurityInfo()
    security.declareObjectPublic()
    template = ViewPageTemplateFile('addrelation_vocabulary.pt')


    @apply
    def vocabulary():
        def get(self):
            return self._vocabulary
        def set(self, value):
            if isinstance(value, str):
                obj = self.context.plone
                self._vocabulary = getUtility(IVocabularyFactory, name=value)(obj)
            elif IVocabularyTokenized.providedBy(value):
                self._vocabulary = value
            else:
                raise AttributeError, "Invalid vocabulary"
        return property(get, set)
    
   

    def getVocabularyItems(self):
        real_terms = []
        for term in self.vocabulary:
            uid =  self.context.context.getIdForObject(term.value)
            if self.context.hasValue(uid):
                continue
            new_term = SimpleTerm(uid, title=term.title)
            real_terms.append(new_term)
        return SimpleVocabulary(real_terms)


initializeClass(PloneRelationVocabularyAddWidget)
