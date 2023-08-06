
The purpose of this extension is to provide formlib widget to edit
plone.app.relation relations. This have been tested with Plone 2.5.

Interface definition
====================

Simple interface for our contents, using the custom Zope 3 field for
relation::

  >>> from infrae.plone.relations.schema import PloneRelation
  >>> from zope.interface import implements, Interface
  >>> class ISimpleContent(Interface):
  ...    """Simple interface with relation."""
  ...    relation = PloneRelation(relation="relation1")


In the user interface, Zope IntID are used to keep track of
object. You can also use Archetype UID (check the ``configure.zcml``
file), in this case all content must comes from the Referenceable
class of Archetype (``Products.Archetypes.Referenceable``).


Widget definition
=================

The plone relation widget is customisable, you can select different
sub-widgets to select new items to add to relation. These sub-widgets
can takes arguments. For instance here, you can put a restriction on
``content_type``.

The widget is built using ``CustomWidgetFactory``::

  >>> from infrae.plone.relations.form import PloneRelationEditWidget
  >>> from infrae.plone.relations.form import PloneRelationSearchAddWidget
  >>> from zope.app.form import CustomWidgetFactory
  >>> widget_factory = CustomWidgetFactory(PloneRelationEditWidget,
  ...                                      add_widget=PloneRelationSearchAddWidget,
  ...                                      add_widget_args=dict(content_type='MySimpleContent'))

Currently, there is three different widgets to add relation: one which
does a catalog search with user input and let select result as object
for relation, one which list objects (from the catalog always), one
which use a Zope 3 vocabulary as input.

The ``infrae.plone.relations.form.utility`` provides simple method to
build these widgets.

Form definition
===============

Now, we will do a simple edit form for this content::

  >>> from Products.Five.formlib import formbase
  >>> from zope.formlib import form
  >>> class EditSimpleContentForm(formbase.EditForm):
  ...    label = 'Edit form'
  ...    description = 'Form to edit relation'
  ...    form_fields = form.Fields(ISimpleContent)
  ...    form_fields['relation'].custom_widget = widget_factory


It's easy ?

Real test
=========

We added this code in the ``example.py`` file, and the form would be
bind to Document. We load it now::

  >>> from Products.Five.zcml import load_string
  >>> load_string("""<configure xmlns="http://namespaces.zope.org/browser">
  ... <page name="relation.html"
  ...       for="infrae.plone.relations.form.example.IPloneRelationExample"
  ...       class="infrae.plone.relations.form.example.PloneRelationEditForm"
  ...       permission="cmf.ModifyPortalContent" />
  ... </configure>""")

And now we can invoke a browser, and login::

  >>> from Products.Five.testbrowser import Browser
  >>> from Products.PloneTestCase.setup import portal_owner, default_password
  >>> browser = Browser()
  >>> browser.open('http://nohost/plone')
  >>> browser.getControl(name='__ac_name').value = portal_owner
  >>> browser.getControl(name='__ac_password').value = default_password
  >>> browser.getControl(name='submit').click()

The front-page is a document, so we should get our form::

  >>> browser.open('http://nohost/plone/front-page/relation.html')
  >>> 'Plone relation edit form' in browser.contents
  True
  
So we can search for Plone in this add widget, and should get one
response, since by default there is only one document with the word
*Plone*, the front page itself::
 
  >>> browser.getControl(name='form.relation.search_value').value='Plone'
  >>> browser.getControl(name='form.relation.search_button').click()

And we got some results::

  >>> add_value = browser.getControl(name='form.relation.add_value:list')
  >>> add_value.getControl('Welcome to Plone').selected = True
  >>> browser.getControl(name='form.relation.add_button').click()
  >>> browser.getControl('Apply').click()
  >>> 'Updated on' in browser.contents
  True

You can look up the ``README.EXT.txt`` file for more tests and examples.

