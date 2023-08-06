====================
dolmen.app.container
====================

`dolmen.app.container` is a collection of tools to work with
containers in Dolmen applications.


Getting started
===============

We import the Grok, request and authentication tools, in order to use
them in our tests::

  >>> from grok import testing
  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.security.testing import Principal, Participation
  >>> from zope.security.management import newInteraction, endInteraction


Namechooser
===========

In order to get a consistent policy concerning the container keys,
`dolmen.app.container` provides a INameChooser adapter, for the
`dolmen.content.IContainer` objects.

We create our container type::

  >>> import dolmen.content

  >>> class Folder(dolmen.content.Container):
  ...   dolmen.content.name('a folderish content')
  ...   dolmen.content.require('dolmen.content.Add')

  >>> testing.grok_component('folder', Folder)
  True

  >>> root = getRootFolder()
  >>> folder = Folder()
  >>> root['folder'] = folder

We now create a simple content type::

  >>> from zope.interface import Interface, implements

  >>> class IDocument(Interface):
  ...   pass

  >>> class Document(dolmen.content.Content):
  ...   dolmen.content.name('a document')
  ...   implements(IDocument)

  >>> testing.grok_component('doc', Document)
  True

  >>> manfred = Document()
  >>> manfred.title = u"Manfred"

To use the namechooser, we simply adapt our container to the
INameChooser interfaces::

  >>> from zope.app.container.interfaces import INameChooser
  >>> chooser = INameChooser(folder)
  >>> chooser
  <dolmen.app.container.namechoosers.NormalizingNameChooser object at ...>
  
If no name is provided, the component uses the object's title to
compute an id::

  >>> chooser.chooseName(name='', object=manfred)
  'manfred'

If a name is provided, it is used if possible::

  >>> chooser.chooseName(name='furry elephant', object=manfred)
  'furry elephant'

If the name already exists, it adds a number at the end of the id. To
do that, the name chooser will try all the values from 0 to 100 and
keep the first successful combination::

  >>> folder['manfred'] = object()
  >>> chooser.chooseName(name='', object=manfred)
  'manfred_1'

If there is no solution, an error is raised::

  >>> for i in range(0, 101):
  ...   folder['manfred_%d' % i] = object()

  >>> chooser.chooseName(name='', object=manfred)
  Traceback (most recent call last):
  ...
  ValueError: Cannot find a unique name based on `manfred` after 100 attemps.


Adding menu
===========

Permissions
-----------

`dolmen.app.container` registers a viewlet listing the
`dolmen.content` factories. It displays the factories allowed in the
container. It checks the principal's permissions in the process.

The viewlet is registered for the 'AboveBody' viewlet manager::

  >>> from dolmen.app.layout import AboveBody
  >>> from dolmen.app.container import AddMenu

  >>> request = TestRequest()
  >>> view = getMultiAdapter((folder, request), name="index")

  >>> manager = AboveBody(folder, request, view)
  >>> manager
  <dolmen.app.layout.master.AboveBody object at ...>

  >>> viewlet = AddMenu(folder, request, view, manager)
  >>> viewlet.update()

As we are currently logged in as Manager, we can see all the
factories::

  >>> for factory in viewlet.factories: print factory['name']
  dolmen.app.container.ftests.Folder
  dolmen.app.container.ftests.Document

We can test the rendering::

  >>> print viewlet.render()
  <dl id="add-menu" class="menu additional-actions">
    <dt>Add to folder</dt>
    <dd>
      <ul>
        <li>
  	<a href="http://127.0.0.1/folder/++add++dolmen.app.container.ftests.Folder"
      id="dolmen-app-container-ftests-Folder">
  	  <img src="http://127.0.0.1/@@/dolmen-content-interfaces-IContainer-contenttype_icon.png" alt="Container" width="16" height="16" border="0" />
  	  <span>a folderish content</span>
  	</a>
        </li>
        <li>
  	<a href="http://127.0.0.1/folder/++add++dolmen.app.container.ftests.Document"
      id="dolmen-app-container-ftests-Document">
  	  <img src="http://127.0.0.1/@@/dolmen-app-container-ftests-IDocument-contenttype_icon.png" alt="Document" width="16" height="16" border="0" />
  	  <span>a document</span>
  	</a>
        </li>
      </ul>
    </dd>
  </dl>

We now log a principal with no privileges::

  >>> endInteraction()
  >>> newInteraction(Participation(Principal('zope.judith')))

If we now try to render the viewlet, the Folder factory should not be
available, as it is protected by the 'dolmen.content.Add'
permission. The Document factory should be available as it's not
protected::

  >>> viewlet.update()
  >>> for factory in viewlet.factories: print factory['name']
  dolmen.app.container.ftests.Document


Contraints
----------

The viewlet also checks the constraints on the container and the
factory.

We now log back our manager::

  >>> endInteraction()
  >>> newInteraction(Participation(Principal('zope.mgr')))

We test to see if everything is back to normal::

  >>> viewlet.update()
  >>> for factory in viewlet.factories: print factory['name']
  dolmen.app.container.ftests.Folder
  dolmen.app.container.ftests.Document

We apply a constraint on the folder. It will only be able to contain
IDocument objects::

  >>> from zope.interface import alsoProvides
  >>> from zope.app.container.constraints import contains

  >>> class IDocumentRepository(Interface):
  ...   contains(IDocument)

  >>> alsoProvides(folder, IDocumentRepository)

We check the respect of the constraint::

  >>> viewlet.update()
  >>> for factory in viewlet.factories: print factory['name']
  dolmen.app.container.ftests.Document


Listing
=======

To complete the container's tools, `dolmen.app.container` registers a
view in charge of displaying the content of a container as a table.

First, we reset the container::

  >>> del root['folder']
  >>> folder = root['folder'] = Folder()

We add all kind of contents::

  >>> folder['manfred'] = Document()
  >>> folder['judith'] = Document()
  >>> folder['subfolder'] = Folder()
  >>> folder['not_dolmen.content.IBaseContent'] = object()

Then, we can query the listing view::

  >>> listing = getMultiAdapter((folder, request), name="folderlisting")
  >>> listing.update()

The table lines are a list of the container values::

  >>> list(listing.values)
  [<dolmen.app.container.ftests.Document object at ...>, <dolmen.app.container.ftests.Document object at ...>, <object object at ...>, <dolmen.app.container.ftests.Folder object at ...>]

The rendering displays links with icons (if existing)::

  >>> print listing.content()
  <div class="folder-listing">
    <h1></h1>
    <div><table class="listing sortable">
    <thead>
      <tr>
        <th>Title</th>
        <th>Modified</th>
      </tr>
    </thead>
    <tbody>
      <tr class="even">
        <td><img src="http://127.0.0.1/@@/dolmen-app-container-ftests-IDocument-contenttype_icon.png" alt="Document" width="16" height="16" border="0" />&nbsp;<a href="http://127.0.0.1/folder/judith">judith</a></td>
        <td>None</td>
      </tr>
      <tr class="odd">
        <td><img src="http://127.0.0.1/@@/dolmen-app-container-ftests-IDocument-contenttype_icon.png" alt="Document" width="16" height="16" border="0" />&nbsp;<a href="http://127.0.0.1/folder/manfred">manfred</a></td>
        <td>None</td>
      </tr>
      <tr class="even">
        <td><a href="http://127.0.0.1/folder/not_dolmen.content.IBaseContent">not_dolmen.content.IBaseContent</a></td>
        <td></td>
      </tr>
      <tr class="odd">
        <td><img src="http://127.0.0.1/@@/dolmen-content-interfaces-IContainer-contenttype_icon.png" alt="Container" width="16" height="16" border="0" />&nbsp;<a href="http://127.0.0.1/folder/subfolder">subfolder</a></td>
        <td>None</td>
      </tr>
    </tbody>
  </table></div>
  </div>


Credits
=======

All Dolmen packages are sponsorised by NPAI (http://www.npai.fr)
