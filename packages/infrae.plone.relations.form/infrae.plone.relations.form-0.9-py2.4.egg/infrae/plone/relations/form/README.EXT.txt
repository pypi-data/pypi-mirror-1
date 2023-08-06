
More test on the formlib widget
===============================

This going to be functional test, so we need a browser::

  >>> from Products.Five.testbrowser import Browser
  >>> from Products.PloneTestCase.setup import portal_owner, default_password
  >>> browser = Browser()
  >>> browser.open('http://nohost/plone')
  >>> browser.getControl(name='__ac_name').value = portal_owner
  >>> browser.getControl(name='__ac_password').value = default_password
  >>> browser.getControl(name='submit').click()

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

The field remenber it's old value::

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

We have a delete button for each entry. We only have one entry, so::

  >>> browser.getControl(name='form.relation.remove_0').click()


Display Form
------------

You can define display form as well, see ``example.py`` for more
information::

  >>> load_string("""<configure xmlns="http://namespaces.zope.org/browser">
  ... <page name="view_relation.html"
  ...       for="infrae.plone.relations.form.example.IPloneRelationExample"
  ...       class="infrae.plone.relations.form.example.PloneRelationViewForm"
  ...       permission="cmf.ModifyPortalContent" />
  ... </configure>""")

And go over this form::

  >>> browser.open('http://nohost/plone/front-page/view_relation.html')
  >>> 'Plone relation view form' in browser.contents
  True
