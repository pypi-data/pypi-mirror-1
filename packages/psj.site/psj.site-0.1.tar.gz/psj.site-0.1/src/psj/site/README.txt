
psj.site - The Plone Scolarly Site
**********************************

The thing, that brings psj.policy, psj.content and psj.theme together.

:Test-Layer: integration

The site properties
===================

The psj.site provides some properties imported from psj.policy::

   >>> self.portal.getProperty('title')
   'Perspectivia Site'

The site helpers
================

Additional transforms
---------------------

The psj.site provides the transforms introduced by psj.policy. There
is now a transform 'odt_to_html'::

   >>> transforms = self.portal.portal_transforms
   >>> 'odt_to_html' in transforms.keys()
   True

The new 'doc_to_html' transform should also exist::

   >>> 'doc_to_html' in transforms.keys()
   True

The 'doc_to_html' transform is now the default for transformations
from 'application/msword' to 'text/html'::

   >>> transforms._findPath('application/msword', 'text/html')[0]
   <Transform at doc_to_html>

There is also a transform available for transformations from .odt and
.doc files to PDF format::

   >>> 'odt_to_pdf' in transforms.keys()
   True

   >>> 'doc_to_pdf' in transforms.keys()
   True

The 'doc_to_pdf' transform is now the default for transformations
from 'application/msword' to 'application/pdf'::

   >>> transforms._findPath('application/msword', 'application/pdf')[0]
   <Transform at doc_to_pdf>


Additional content types
------------------------

The psj.site provides the `PSJ Document` type added by psj.content::

   >>> ptypes = self.portal.portal_types
   >>> 'PSJ Document' in ptypes.keys()
   True

Working with PSJ sites
======================

The main focus of Perpectivia or Plone Scholarly Journal sites lies
on handling of external office documents. We setup a testbrowser and
log into the site::

   >>> from Products.Five.testbrowser import Browser
   >>> browser = Browser()
   >>> portal_url = self.portal.absolute_url()
   >>> browser.handleErrors = False
   >>> self.portal.error_log._ignored_exceptions = ()

Finally, we need to log in as the portal owner, i.e. an administrator user. We
do this from the login page::

   >>> from Products.PloneTestCase.setup import portal_owner, default_password

   >>> browser.open(portal_url + '/login_form?came_from=' + portal_url)
   >>> browser.getControl(name='__ac_name').value = portal_owner
   >>> browser.getControl(name='__ac_password').value = default_password
   >>> browser.getControl(name='submit').click()


Working with PSJ documents
--------------------------

PSJ documents can be added anywhere and contain the real documents
(office documents in odf or doc format)::

   >>> browser.open(portal_url)

Verify, that we have the links to create PSJ documents, from the 'add
item menu'::

   >>> browser.getLink(id='psj-document').url.endswith(
   ...   'createObject?type_name=PSJ+Document')
   True

Now let as add a PSJ document without any file::

   >>> browser.getLink(id='psj-document').click()
   >>> browser.getControl(name='title').value = "My first document"
   >>> browser.getControl(name='description').value = "The description"
   >>> browser.getControl(name='form_submit').click()

The created document should be available in the ZODB now::

   >>> 'my-first-document' in list(self.portal.keys())
   True


Adding odt documents
--------------------

Perspectivia sites are able to handle content of many encodings and
several office document types. To do this, office documents are
transformed to HTML which can be watched on the pages displayed. We
Create a simple document by uploading a test document in odt
format. For this we have to return to the edit view again::

   >>> browser.getLink('Edit').click()

We get the testdoc source::

   >>> import os
   >>> testdocpath = os.path.dirname(os.path.abspath(__file__))
   >>> testdocpath = os.path.join(testdocpath, 'tests')
   >>> docpath = os.path.join(testdocpath, 'simpledoc.odt')

   >>> import cStringIO
   >>> myfile = cStringIO.StringIO(str(open(docpath, 'rb').read()))

And upload::

   >>> file_ctrl = browser.getControl(name="document_file")
   >>> file_ctrl.add_file(myfile, 'application/vnd.oasis.opendocument.text',
   ...                    filename='simpledoc.odt')
   >>> browser.getControl(name='form_submit').click()

We can see the document now as HTML representation::

   >>> print browser.contents
   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"...
   ...A simple document....
   ...</html>

The file was also automatically transformed to a PDF file, which is
available for download in the normal view::

   >>> print browser.contents
   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"...
   ...
   <a href="http://nohost/plone/my-first-document/at_download/pdfdocument">
           <img src="http://nohost/plone/pdf.png" />
                simpledoc.pdf
           </a>
           <span class="discreet">
                &mdash;
                PDF document,
                ...Kb
           </span>
   ...


Adding doc documents
--------------------

Also MS word documents are handled. As for odt documents, they are
processed by OOo and the output afterwards filtered by tidy. We browse
to the edit view again and upload a word document::

   >>> browser.getLink('Edit').click()
   >>> docpath = os.path.join(testdocpath, 'simpledoc.doc')
   >>> myfile = cStringIO.StringIO(str(open(docpath, 'rb').read()))
   >>> file_ctrl = browser.getControl(name="document_file")
   >>> file_ctrl.add_file(myfile, 'application/msword',
   ...                    filename='simpledoc.doc')

Before submitting the form, we must make sure, that we enabled the
radio button for upload. This shows up only, if we change an
associated file::

   >>> browser.getControl(name='document_delete').value = ['']
   >>> browser.getControl(name='form_submit').click()

We can see the document now as HTML representation::

   >>> print browser.contents
   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"...
   ...A simple document....
   ...</html>

The file was also automatically transformed to a PDF file, which is
available for download in the normal view::

   >>> print browser.contents
   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"...
   ...
   <a href="http://nohost/plone/my-first-document/at_download/pdfdocument">
           <img src="http://nohost/plone/pdf.png" />
                simpledoc.pdf
           </a>
           <span class="discreet">
                &mdash;
                PDF document,
                ...Kb
           </span>
   ...


Handling 'exotic' charsets and encodings
----------------------------------------

PSJ documents can display documents with non-standard encodings, like
japanese, cyrillic or arabic text. We upload a test document that
contains this three types of text::

   >>> browser.getLink('Edit').click()
   >>> docpath = os.path.join(testdocpath, 'alientext.odt')
   >>> myfile = cStringIO.StringIO(str(open(docpath, 'rb').read()))
   >>> file_ctrl = browser.getControl(name="document_file")
   >>> file_ctrl.add_file(myfile, 'application/vnd.oasis.opendocument.text',
   ...                    filename='alientext.odt')
   >>> browser.getControl(name='document_delete').value = ['']
   >>> browser.getControl(name='form_submit').click()

We can see the different charsets in the HTML:

- arabic text::

   >>> 'xml:lang="ar-SA">\xd8\xa7\xd9\x84\xd8\xa7\xd8' in browser.contents
   True

- cyrillic text::

   >>> '\xd1\x81\xd0\xbc\xd0\xb5\xd1\x8f' in browser.contents
   True

- japanese text::

   >>> u'\u304a\u732b\u3055\u307e' in browser.contents.decode('utf-8')
   True

