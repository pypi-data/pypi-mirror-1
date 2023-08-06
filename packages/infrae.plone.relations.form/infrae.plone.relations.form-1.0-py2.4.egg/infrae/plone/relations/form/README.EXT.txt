
More test on the formlib widget
===============================

This going to be functional test, so we need a browser::

  >>> browser = self.getAuthenticatedBrowser()


Add with search
---------------

Let's load some ZCML, for more test on edition::

  >>> from Products.Five.zcml import load_string
  >>> load_string("""<configure xmlns="http://namespaces.zope.org/browser">
  ... <page name="edit_relation.html"
  ...       for="infrae.plone.relations.form.example.IPloneRelationExample"
  ...       class="infrae.plone.relations.form.example.PloneRelationEditForm"
  ...       permission="cmf.ModifyPortalContent" />
  ... </configure>""")

And move on the form::

  >>> browser.open('http://nohost/plone/front-page/edit_relation.html')
  >>> 'Plone relation edit form' in browser.contents
  True

First, the field is required, so we get an error if we don't fill a value::

  >>> browser.getControl('Apply').click()
  >>> 'There were errors' in browser.contents
  True

We can add new relation, so get we get the corresponding form, but
there is no current relation::

  >>> 'New relation' in browser.contents
  True
  >>> 'Current relation' in browser.contents
  False

So we can search for Plone. We would find only the front-page, since
it's the only document by default and add it::

  >>> browser.getControl(name='form.relation.search_value').value='Plone'
  >>> browser.getControl(name='form.relation.search_button').click()
  >>> add_value = browser.getControl(name='form.relation.add_value:list')
  >>> len(add_value.options)
  1
  >>> add_value.getControl('Welcome to Plone').selected = True
  >>> browser.getControl(name='form.relation.add_button').click()

The field remember it's old value::

 >>> browser.getControl(name='form.relation.search_value').value
 'Plone'

And we have relations now::

  >>> 'Current relation' in browser.contents
  True

After we added this, if we research for documents it's not going to be
re-proposed, even the form won't be display since there is no more
item matching the request::

  >>> browser.getControl(name='form.relation.search_button').click()
  >>> browser.getControl(name='form.relation.add_value:list')
  Traceback (most recent call last):
    ...
  LookupError: name 'form.relation.add_value:list'

And we save::

  >>> browser.getControl('Apply').click()
  >>> 'Updated on' in browser.contents
  True


Delete an entry
---------------

We have a delete button for each entry. We only have one entry, so
after deletion none left::

  >>> browser.getControl(name='form.relation.remove_0').click()
  >>> 'Current relation' in browser.contents
  False

Display Form
------------

You can define display form as well, see ``example.py`` for more
information::

  >>> load_string("""<configure xmlns="http://namespaces.zope.org/browser">
  ... <page name="view_relation.html"
  ...       for="infrae.plone.relations.form.example.IPloneRelationExample"
  ...       class="infrae.plone.relations.form.example.PloneRelationViewForm"
  ...       permission="zope2.View" />
  ... </configure>""")

And go over this form::

  >>> browser.open('http://nohost/plone/front-page/view_relation.html')
  >>> 'Plone relation view form' in browser.contents
  True


Edit form with an context object
--------------------------------

You can attach data to your relation. Load an edit form for folders::

  >>> load_string("""<configure xmlns="http://namespaces.zope.org/browser">
  ... <page name="edit_context.html"
  ...       for="infrae.plone.relations.form.example.IPloneRelationCtxtExample"
  ...       class="infrae.plone.relations.form.example.PloneRelationCtxtEditForm"
  ...       permission="cmf.ModifyPortalContent" />
  ... </configure>""")

This relation accept only published folders, can only have one item.
Create some folder on the root as test material::

  >>> self.createFolder(self.portal, 'Folder 1', published=True)
  >>> self.createFolder(self.portal, 'Folder 2', published=True)
  >>> self.createFolder(self.portal, 'Folder 3', published=False)

So you get an edit form on a folder::

  >>> browser.open('http://nohost/plone/folder-1/edit_context.html')
  >>> 'Plone relation edit form with context' in browser.contents
  True

You can add a new relation::

  >>> 'New relation' in browser.contents
  True

Since it's a list widget, we already have the adding list, with our
two published folders::

  >>> add_value = browser.getControl(name='form.relation.add_value:list')
  >>> len(add_value.options)
  2
  >>> add_value.getControl('Folder 3')
  Traceback (most recent call last):
    ...
  LookupError: label 'Folder 3'
  >>> add_value.getControl('Folder 2').selected = True

But we need to fill the context information, before adding the relation::

  >>> browser.getControl('Float value').value = '5.0'
  >>> browser.getControl('String value').value = 'Hello'
  >>> browser.getControl(name='form.relation.add_button').click()

Now you get one relation, and since it's limited to one, you can't add an other one::

  >>> 'New relation' in browser.contents
  False
  >>> 'Current relation' in browser.contents
  True

After, you can edit context data::
  
  >>> browser.getControl(name='form.relation.modify_0').click()
  >>> browser.getControl(name='form.relation.modify_0')
  Traceback (most recent call last):
    ...
  LookupError: name 'form.relation.modify_0'  
  >>> browser.getControl('Float value').value
  '5.0'
  >>> browser.getControl('String value').value
  'Hello'

If we put an invalid data, validation on sub-widget works::

  >>> browser.getControl('Float value').value = 'Invalid'
  >>> browser.getControl(name='form.relation.modify_apply').click()
  >>> 'Invalid floating point data' in browser.contents
  True
  >>> browser.getControl('Float value').value = '42'
  >>> browser.getControl('String value').value = ''
  >>> browser.getControl(name='form.relation.modify_apply').click()
  >>> 'Required input is missing' in browser.contents
  True
  >>> browser.getControl('String value').value = 'World'
  >>> browser.getControl(name='form.relation.modify_apply').click()
  >>> browser.getControl(name='form.relation.modify_0').click()
  >>> browser.getControl('Float value').value
  '42.0'
  >>> browser.getControl('String value').value
  'World'
  >>> browser.getControl(name='form.relation.modify_apply').click()

Save the whole edition::

  >>> browser.getControl('Apply').click()
  >>> 'Updated on' in browser.contents
  True

Edit form using a vocabulary
----------------------------

First, register the form and the used vocabulary::


  >>> load_string("""<configure xmlns="http://namespaces.zope.org/zope"
  ...            xmlns:browser="http://namespaces.zope.org/browser">
  ... <vocabulary factory="infrae.plone.relations.form.example.MyVocabulary"
  ...             name="My vocabulary" />
  ... <browser:page name="edit_vocabulary.html"
  ...               for="infrae.plone.relations.form.example.IPloneRelationVocExample"
  ...               class="infrae.plone.relations.form.example.PloneRelationVocEditForm"
  ...               permission="cmf.ModifyPortalContent" />
  ... </configure>""")


We need some documents in a folder::

  >>> self.createFolder(self.portal, 'Folder')
  >>> self.createDocument(self.portal.folder, 'Document 1', 'Babelfish')
  >>> self.createDocument(self.portal.folder, 'Document 2', 'In the sky')
  >>> self.createDocument(self.portal.folder, 'Document 3', 'Fly very high')

We should get the form on a folder::

  >>> browser.handleErrors = False
  >>> browser.open('http://nohost/plone/folder/edit_vocabulary.html')
  >>> 'Plone relation edit form based on a vocabulary' in browser.contents
  True
  >>> 'New relation' in browser.contents
  True

Now, we can select values coming from our vocabulary::

  >>> add_value = browser.getControl(name='form.relation.add_value:list')
  >>> len(add_value.options)
  3
  >>> add_value.getControl('Document 1').selected = True
  >>> add_value.getControl('Document 2').selected = True
  >>> add_value.getControl('Welcome to Plone')
  Traceback (most recent call last):
    ...
  LookupError: label 'Welcome to Plone'
  >>> browser.getControl(name='form.relation.add_button').click()

So we get our relation::

  >>> 'New relation' in browser.contents
  True
  >>> 'Current relation' in browser.contents
  True
  >>> add_value = browser.getControl(name='form.relation.add_value:list')
  >>> len(add_value.options)
  1

And we can save it::

  >>> browser.getControl('Apply').click()
  >>> 'Updated on' in browser.contents
  True
