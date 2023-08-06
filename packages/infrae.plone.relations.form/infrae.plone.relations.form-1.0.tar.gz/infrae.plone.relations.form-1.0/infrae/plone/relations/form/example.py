# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: example.py 29203 2008-06-13 13:07:10Z sylvain $

# Define an interface with fields.
from zope.interface import Interface
from infrae.plone.relations.schema import PloneRelation


class IPloneRelationExample(Interface):
    """An example for plone relation.
    """

    relation = PloneRelation(title=u"Relation field",
                             description=u"Field with a relation",
                             relation="plone relation",
                             unique=True)



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



# More advanced relation, with context object, first define a
# interface for the context object.
from zope import schema

class IPloneRelationContext(Interface):
    float_value = schema.Float(title=u"Float value")
    string_value = schema.TextLine(title=u"String value")


# And make a new interface using a relation with a context object.
class IPloneRelationCtxtExample(Interface):

    relation = PloneRelation(title=u"Relation with a context",
                             relation="relation context",
                             context_schema=IPloneRelationContext,
                             unique=True,
                             required=False,
                             max_length=1)



# And provide an implementation. BasePloneRelationContext is a helper
# if you use Archetype UID to reference object, but the default is to
# use Zope IntID, so SimpleItem is sufficient as base class.
from infrae.plone.relations.schema import BasePloneRelationContext
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

class PloneRelationContext(BasePloneRelationContext):
    implements(IPloneRelationContext)

    float_value = FieldProperty(IPloneRelationContext["float_value"])
    string_value = FieldProperty(IPloneRelationContext["string_value"])



# We can define a new widget, with a list. We use the helper as well.
from infrae.plone.relations.form.utility import buildListAddWidget
from infrae.plone.relations.schema import BasePloneRelationContextFactory

context_factory = BasePloneRelationContextFactory(PloneRelationContext,
                                                  IPloneRelationContext)
widget_factory_ctxt = buildListAddWidget('Folder',
                                         context_factory=context_factory,
                                         review_state='published')


# And create a form for it.
class PloneRelationCtxtEditForm(formbase.EditForm):
    label = 'Plone relation edit form with context'
    description = 'Form to edit with relations with context'
    form_fields = form.Fields(IPloneRelationCtxtExample)
    form_fields['relation'].custom_widget = widget_factory_ctxt


# And add this interface to a folder. Since the context object are
# created as Zope object, you need a folderish item to set them. You
# could imagine an other factory setting them as annotation to the
# object.
from Products.ATContentTypes.content.folder import ATFolder
classImplements(ATFolder, IPloneRelationCtxtExample)


# And now, an example with a vocabulary.
class IPloneRelationVocExample(Interface):

    relation = PloneRelation(title=u"Relation based on a vocabulary",
                             relation="relation vocabulary",
                             required=False)


# We can define a new widget, with a list. We use the helper as well.
from infrae.plone.relations.form.utility import buildVocabularyAddWidget

widget_factory_voc = buildVocabularyAddWidget("My vocabulary")

# And make a new form for it.
class PloneRelationVocEditForm(formbase.EditForm):
    label = 'Plone relation edit form based on a vocabulary'
    description = 'Form using vocabulary'
    form_fields = form.Fields(IPloneRelationVocExample)
    form_fields['relation'].custom_widget = widget_factory_voc


# And bind the form on folder for example.
classImplements(ATFolder, IPloneRelationVocExample)


# And implement a vocabulary...
from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

class MyVocabularyFactory(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        # you can do what ever you here, just return a vocabulary with objects.
        items = context.portal_catalog(portal_type='Document',
                                       path=dict(query='/'.join(context.getPhysicalPath()),
                                                 depth=1))
        terms = [SimpleTerm(e.getObject(), token=e.getId, title=e.Title) for e in items]
        return SimpleVocabulary(terms)

MyVocabulary = MyVocabularyFactory()
