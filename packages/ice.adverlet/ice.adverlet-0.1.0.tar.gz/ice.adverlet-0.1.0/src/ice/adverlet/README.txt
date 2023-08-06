============
ice.adverlet
============

.. contents::

Usage
=====

This package - for Zope3 based sites - provides a simple way to edit
any HTML snippet. It includes a WYSIWYG-editor, undo support and
storage for images.

Examples of possible uses include: advertisement portlets,
announcements, footers, frontpages, etc.

The package provides the ZCML directive `adverlet` and TALES
expression `adverlet`.

To use the package follow these 6 simple steps:

1) Include the package:

   <include package="ice.adverlet" file="meta.zcml" />
   <include package="ice.adverlet" />

2) In the ZCML configuration file define all your adverlets, for
example:

   <ice:adverlet name="top" />

   <ice:adverlet
       name="bottom"
       description="This is an advertisement at the bottom of the frontpage"
       />

   <ice:adverlet
       name="footer"
       description="Footer of the site"
       default="default-footer"
       />

Notice:
`name` - Required.
`description` - Not required.
`default` - Not required, it is name of browser view, registered b
zcml-directives like browser:page.

3) Write `adverlet` TALES expression in to your skin:

  <div tal:content="structure adverlet:top" />

where `top` is name of the adverlet.

4) The package provides a view to manage all registered adverlets.
This view may be called by a special content provider
in any page::

  <div tal:content="structure provider:ice.adverlet.manage" />

5) This content provider has the permission "ice.adverlet.Manage".
Therefore, you need to grant this permission to a role in your
project, and allow "undo" for this user, for example::

<grant permission="ice.adverlet.Manage" role="foo.blah.Blah" />
<grant permission="zope.UndoOwnTransactions" role="foo.blah.Blah" />

6) Install and register 2 local utilities:

 1. Factory - ice.adverlet.storage.SourceStorage;
    Interface - ice.adverlet.interfaces.ISourceStorage;
    Name - empty.
    (into Local Site Manager)

 2. Factory - ice.adverlet.storage.FileStorage;
    Interface - ice.adverlet.interfaces.IFileStorage;
    Name - empty.
    (into local site)

That's it!

N.B. You can define your own templates for management UI.
To do this, take a look at ice/adverlet/browser/template
and write your own adapters in your project for your own templates.

You will need to:

- Change @adapter(IContentProvider, IDefaultBrowserLayer)
  to @adapter(IContentProvider, IMyCustomLayer)
- Register this adapter with the same name
  (take a look at ice/adverlet/browser/configure.zcml,
  section <!-- templates -->.)


Tests
=====

  >>> import zope.interface
  >>> import zope.component

Let's register a default view for one of our adverlets::

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()
  >>> templateFileName = os.path.join(temp_dir, 'default_footer.pt')
  >>> open(templateFileName, 'w').write('''
  ... <h1>Default Footer</h1>
  ... ''')

  >>> from zope.publisher.interfaces import browser
  >>> from zope.app.pagetemplate import simpleviewclass
  >>> DefaultViewClass = simpleviewclass.SimpleViewClass(
  ...     templateFileName, name='default-footer')

  >>> zope.component.provideAdapter(
  ...     DefaultViewClass,
  ...     (zope.interface.Interface, browser.IDefaultBrowserLayer),
  ...     zope.interface.Interface,
  ...	  name='default-footer'
  ...	  )

Let's register a few advertlets::

  >>> from zope.configuration import xmlconfig
  >>> import ice.adverlet
  >>> context = xmlconfig.file('meta.zcml', ice.adverlet)

  >>> context = xmlconfig.string('''
  ...     <configure
  ...	      xmlns="http://namespaces.zope.org/zope"
  ...	      xmlns:ice="http://namespaces.zope.org/ice"
  ...	      i18n_domain="test">
  ...
  ...	      <ice:adverlet
  ...	          name="frontpage"
  ...		  />
  ...
  ...	      <ice:adverlet
  ...             name="footer"
  ...		  description="Footer of the site"
  ...		  default="default-footer"
  ...		  />
  ...
  ...     </configure>''', context)

Now we can try to call these adverlets in any view::

  >>> templateFileName = os.path.join(temp_dir, 'template.pt')
  >>> open(templateFileName, 'w').write('''
  ... <html>
  ... <body>
  ... <div tal:content="structure adverlet:frontpage" />
  ... <div tal:content="structure adverlet:footer" />
  ... </body>
  ... </html>
  ... ''')

  >>> PageClass = simpleviewclass.SimpleViewClass(
  ...     templateFileName, name='index.html')

  >>> zope.component.provideAdapter(
  ...     PageClass,
  ...     (zope.interface.Interface, browser.IDefaultBrowserLayer),
  ...     zope.interface.Interface,
  ...	  name='index.html'
  ...	  )

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> class Content(object):
  ...     zope.interface.implements(zope.interface.Interface)
  >>> content = Content()

  >>> view = zope.component.getMultiAdapter(
  ...     (content, request), name='index.html')

  >>> print view().strip()
  <html>
  <body>
  <div></div>
  <div>
  <h1>Default Footer</h1>
  </div>
  </body>
  </html>
  <BLANKLINE>

To edit adverlets store HTML sources::

  >>> from ice.adverlet.storage import SourceStorage
  >>> from ice.adverlet.interfaces import ISourceStorage

  >>> storage = SourceStorage()
  >>> ISourceStorage.providedBy(storage)
  True

  >>> storage.sources['frontpage'] = u'''
  ...     <h2><a href="http://launchpad.net>Launchpad</a></h2>
  ...	  '''
  >>> storage.sources['footer'] = u'''
  ...	  <h3><a href="http://ohloh.net>OhLoh</a></h3>
  ...	  '''

and register storage as utility::

  >>> zope.component.provideUtility(storage, ISourceStorage)

Let's check the test view now::

  >>> print view().strip()
  <html>
  <body>
  <div>
  <h2><a href="http://launchpad.net>Launchpad</a></h2>
  </div>
  <div>
  <h3><a href="http://ohloh.net>OhLoh</a></h3>
  </div>
  </body>
  </html>
  <BLANKLINE>

Then we will test image storage and image wrapper.
To do this, let's register storage for the files::

  >>> from ice.adverlet.storage import FileStorage
  >>> from ice.adverlet.interfaces import IFileStorage

  >>> files = FileStorage()
  >>> IFileStorage.providedBy(files)
  True

  >>> zope.component.provideUtility(files, IFileStorage)

And let's try to use the image wrapper to store images in this storage::

  >>> from ice.adverlet.image import ImageWrapper
  >>> from ice.adverlet.interfaces import IImageWrapper

  >>> wrapper = ImageWrapper()
  >>> IImageWrapper.providedBy(wrapper)
  True

Register adapter for DublinCore::

  >>> from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
  >>> from zope.dublincore.interfaces import IZopeDublinCore
  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> from zope.app.file.image import Image

  >>> zope.interface.classImplements(Image, IAttributeAnnotatable)

  >>> zope.component.provideAdapter(
  ...     factory = ZDCAnnotatableAdapter,
  ...	  provides = IZopeDublinCore,
  ...	  adapts = (IAttributeAnnotatable,)
  ...	  )

We use test image::

  >>> from ice.adverlet.tests.tests import zptlogo
  >>> wrapper.data = zptlogo
  >>> wrapper.description = u'Logo image'

Now let's check file storage::

  >>> [key for key in files.keys()]
  [u'Image']

  >>> [IZopeDublinCore(file).title for file in files.values()]
  [u'Logo image']

Note that in management UI we use named global utilities IAdverlet
for store HTML instead of using the storage directly. Let's test
this feature::

  >>> storage.sources['frontpage']
  u'\n    <h2><a href="http://launchpad.net>Launchpad</a></h2>\n    '

  >>> from ice.adverlet.interfaces import IAdverlet
  >>> frontpage = zope.component.getUtility(IAdverlet, 'frontpage')

  >>> frontpage.source = '<h2>Hi there</h2>'

  >>> storage.sources['frontpage']
  '<h2>Hi there</h2>'

And let's check adverlet again::

  >>> frontpage.source
  '<h2>Hi there</h2>'

We provide event for modify sources::

  >>> events = []
  >>> zope.component.provideHandler(events.append, (None, ))

  >>> frontpage.source = '<h2>Welcome!</h2>'

  >>> events
  [<ice.adverlet.events.SourceModifiedEvent instance at ...>]

The event holds the name of the global `adverlet` utility::

  >>> events[0].name
  u'frontpage'

Finally we look up test browser class again::

  >>> print view().strip()
  <html>
  <body>
  <div><h2>Welcome!</h2></div>
  <div>
  <h3><a href="http://ohloh.net>OhLoh</a></h3>
  </div>
  </body>
  </html>
  <BLANKLINE>

Cleanup::

  >>> import shutil
  >>> shutil.rmtree(temp_dir)
