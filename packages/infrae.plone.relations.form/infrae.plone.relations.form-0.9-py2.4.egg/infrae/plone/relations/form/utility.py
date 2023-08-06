# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: utility.py 29119 2008-06-11 10:34:14Z sylvain $

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: utility.py 29119 2008-06-11 10:34:14Z sylvain $"


from zope.app.form import CustomWidgetFactory

from infrae.plone.relations.form import PloneRelationEditWidget
from infrae.plone.relations.form import PloneRelationSearchAddWidget, PloneRelationListAddWidget
from infrae.plone.relations.form import PloneRelationVocabularyAddWidget
from infrae.plone.relations.schema import BasePloneRelationContextFactory as PRCF


def buildListAddWidget(content_type, review_state=None, context_factory=None):
    """Utility to get shorter code in forms.
    """
    return CustomWidgetFactory(PloneRelationEditWidget,
                               add_widget=PloneRelationListAddWidget,
                               add_widget_args=dict(content_type=content_type,
                                                    review_state=review_state),
                               context_factory=context_factory)


def buildSearchAddWidget(content_type, review_state=None, context_factory=None):
    """Utility to get shorter code in forms.
    """
    return CustomWidgetFactory(PloneRelationEditWidget,
                               add_widget=PloneRelationSearchAddWidget,
                               add_widget_args=dict(content_type=content_type,
                                                    review_state=review_state),
                               context_factory=context_factory)

def buildVocabularyAddWidget(vocabulary, context_factory=None):
    """Utility to get shorter code in forms.
    """
    return CustomWidgetFactory(PloneRelationEditWidget,
                               add_widget=PloneRelationVocabularyAddWidget,
                               add_widget_args=dict(vocabulary=vocabulary),
                               context_factory=context_factory)
