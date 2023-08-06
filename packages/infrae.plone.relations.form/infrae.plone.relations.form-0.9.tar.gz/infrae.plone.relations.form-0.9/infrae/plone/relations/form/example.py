# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: example.py 29164 2008-06-12 13:02:07Z sylvain $

# Define an interface with fields.
from zope.interface import Interface
from infrae.plone.relations.schema import PloneRelation


class IPloneRelationExample(Interface):
    """An exemple for plone relation.
    """

    relation = PloneRelation(title=u"Relation field",
                             description=u"Field with a relation",
                             relation="plone relation")


# Define a search widget.

from infrae.plone.relations.form import PloneRelationEditWidget
from infrae.plone.relations.form import PloneRelationSearchAddWidget
from zope.app.form import CustomWidgetFactory

widget_factory = CustomWidgetFactory(PloneRelationEditWidget,
                                     add_widget=PloneRelationSearchAddWidget,
                                     add_widget_args=dict(content_type='Document'))


# Define an edition form.
from Products.Five.formlib import formbase
from zope.formlib import form

class PloneRelationEditForm(formbase.EditForm):
    label = 'Plone relation edit form'
    description = 'Form to edit with relations'
    form_fields = form.Fields(IPloneRelationExample)
    form_fields['relation'].custom_widget = widget_factory


# Define an view form.
class PloneRelationViewForm(formbase.DisplayForm):
    label = 'Plone relation view form'
    description = 'Form to view relations'
    form_fields = form.Fields(IPloneRelationExample)


# We are going to add this interface to documents
from Products.ATContentTypes.content.document import ATDocument
from zope.interface import classImplements

classImplements(ATDocument, IPloneRelationExample)

