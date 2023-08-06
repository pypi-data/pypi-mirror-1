==========
README.txt
==========

largeblue.pages aims to solve a fairly common, relatively simple web development
requirement:

* all or some of a website's pages need to be editable via a WYSIWYG editor
  (e.g.: by a client or non-technical website administrator)
* however, the site's developer(s) most definitely do not want to edit the 
  pages' content via a WYSIWYG editor, they (you) want to use their (your) 
  normal text editor and possibly version control, etc.
* some pages of the website may not be appropriate to be editable via a WYSIWYG 
  (e.g.: where javascript is being used on a specific markup structure for a
  bespoke page)
* the website structure should ideally be flexible, so new pages and sections 
  can be added recursively without re-development

largeblue.pages:

* provides Page Container and Page content objects, where pages can contain any
  number of sub pages and so on ad infinitum
* a Page's content property is setup to be edited by a WYSIWYG editor (in fact, 
  we configure and patch the default z3c.widget.tiny WYSIWYG widget to make sure 
  it stores valid xhtml and that the output source code nesting has each element 
  indented by 2 spaces)
* each Page and it's html content can also be accessed by webdav (largeblue.pages 
  uses bebop.webdav's patching of zope.app.dav / z3c.dav to provide read and write 
  webdav access) so that a page appears as a folder, containing a main_content.html 
  and any number of other page folders.  This way, the whole structure of pages 
  can be edited without going near a web browser.

There are some other useful features:

* @@edit.html and @@ordering.html are custom ZMI views hung off a page that can 
  be added to an admin skin, where the @@ordering.html (called 'Manage Contents')
  provides a custom, orderable container view, so pages can be moved up and down
  as well as renamed, cut pasted, deleted and added, etc.
* every Page Container has a property called 'index' that, at any time, contains a 
  snapshot of the current pages structure (it's updated whenever a Page created, 
  modified or deleted event happens) - note, you can have multiple page containers 
  are they all maintain their own index
* the obj.__name__ of each page is forced to be a sane 'no cross browser href
  issues' snippet of text
* pages have a flag attribute, intended to be referenced in a view class (see 
  ./browser/index.py) to control whether they are 'simple' pages which just render 
  the managable content or bespoke pages that need to be special cased

To use largeblue.pages, you'll just need to add the package to your site.zcml (or equivalent)::

    <include package="largeblue.pages" />
    <includeOverrides package="largeblue.pages" file="overrides.zcml" />

I'd imagine that you'll want to expose one or more views on the IPage object, ala...

    <browser:page name="index.html"
        for="largeblue.pages.interfaces.IPage"
        class="..my.IndexView"
        permission="zope.View"
    />
    
... where your IndexView can use the flag attribute to determine whether to use the WYSIWYG managable content, or do something else entirely (e.g.: use a custom template).

Anyway, let's see it in action.
    
    >>> import transaction, pprint
    >>> from zope.component import createObject
    >>> from zope.event import notify
    >>> from zope.lifecycleevent import ObjectCreatedEvent
    >>> from zope.lifecycleevent import ObjectModifiedEvent
    >>> from bebop.ordering.interfaces import IOrdering, IOrderable
    >>> from largeblue.pages.interfaces import IPage, IPageContainer, IFile
    >>> from largeblue.pages.page import PageContainer

Create a page container.
    
    >>> app['pages'] = PageContainer()

Create a page.

    >>> page1 = createObject('largeblue.pages.Page')
    >>> page1.__name__ = 'page1'
    >>> page1.title = u'Page 1'
    >>> for item in page1:
    ...     print item
    ...
    >>> page1.content
    u''
    >>> page1.flag
    u'Static'
    
Add it to the container and fire a created event.

    >>> app['pages']['page1'] = page1
    >>> notify(ObjectCreatedEvent(page1))
    
And we see it now contains a file called html_content.html and that this is
editable via the Page's content property.
    
    >>> page1 = app['pages']['page1']
    >>> for item in page1:
    ...     print item
    ...
    main_content.html
    >>> page1['main_content.html'].contentType
    'text/html'
    >>> page1.content
    '<div>Under construction</div>'
    >>> page1['main_content.html'].data
    '<div>Under construction</div>'
    >>> page1['main_content.html'].data = '<div>Foo bar</div>'
    >>> page1['main_content.html'].data
    '<div>Foo bar</div>'
    >>> page1.content
    '<div>Foo bar</div>'
    >>> page1.content = '<div>Under construction</div>'
    >>> page1.content
    '<div>Under construction</div>'
    >>> page1['main_content.html'].data
    '<div>Under construction</div>'

Let's look at the Page Container's index property:

    >>> pages = app['pages']
    >>> for item in pages:
    ...     print item
    ...
    page1
    >>> pages.index
    [{'title': u'Page 1', 'pages': [], 'label': u'page1'}]
    >>> page2 = createObject('largeblue.pages.Page')
    >>> page2.__name__ = 'movies'
    >>> page2.title = u'Movies'
    >>> pages['movies'] = page2
    >>> for item in pages:
    ...     print item
    ...
    movies
    page1
    >>> notify(ObjectCreatedEvent(page2))
    >>> pages.index
    [{'title': u'Page 1', 'pages': [], 'label': u'page1'}, {'title': u'Movies', 'pages': [], 'label': u'movies'}]

We can nest Pages within Pages:

    >>> page3 = createObject('largeblue.pages.Page')
    >>> page3.__name__ = 'horror'
    >>> page3.title = u'Scary Horror Films'
    >>> notify(ObjectCreatedEvent(page3))
    >>> pages['movies']['horror'] = page3
    >>> page4 = createObject('largeblue.pages.Page')
    >>> page4.__name__ = 'texas'
    >>> page4.title = u'The Texas Chainsaw Massacre'
    >>> notify(ObjectCreatedEvent(page4))
    >>> pages['movies']['horror']['texas'] = page4

Check the index again:

    >>> pprint.pprint(pages.index)
    [{'title': u'Page 1', 'pages': [], 'label': u'page1'},
     {'label': u'movies',
      'pages': [{'label': u'horror',
                 'pages': [{'label': u'texas',
                            'pages': [],
                            'title': u'The Texas Chainsaw Massacre'}],
                 'title': u'Scary Horror Films'}],
      'title': u'Movies'}]

The idea is that the index can be referenced by a dynamic navigation, say, without having to traverse the Pages' heirarchy every time.  Key to this is the ability to order the pages, so you can control the order in which the navigation items are displayed.

We've patched bebop.ordering to achieve just this.  Let's look at the root container's order:

    >>> IOrdering(pages).getNames()
    [u'page1', u'movies']
    >>> IOrdering(pages).keys()
    [0, 1]
    >>> IOrdering(pages).upOne([1])
    >>> IOrdering(pages).getNames()
    [u'movies', u'page1']
    >>> notify(ObjectModifiedEvent(pages))
    >>> pprint.pprint(pages.index)
    [{'label': u'movies',
      'pages': [{'label': u'horror',
                 'pages': [{'label': u'texas',
                            'pages': [],
                            'title': u'The Texas Chainsaw Massacre'}],
                 'title': u'Scary Horror Films'}],
      'title': u'Movies'},
      {'title': u'Page 1', 'pages': [], 'label': u'page1'}]
    
There's more in bebop.ordering.README.txt on this.  What we've done is limited the orderable contents of an Ordering container to *only include pages*:

    >>> for item in page3:
    ...    print item
    ...
    main_content.html
    texas
    >>> IOrdering(page3).getNames()
    [u'texas']

Plus we've extended the functionality of the ordering container view to accomodate the 'normal' actions too.  This way, an admin skin ZMI layer need only expose the @@edit.html and @@ordering.html views on the Page, thus hiding anything other than Pages in the Page container view (e.g.: main_content.html, .svn files, etc.).

To connect via webdav to the Pages structure, simply connect to your site instance, eg: http://localhost:8080 and, voila, you'll see a structure like:

- pages
  - page1
    - main_content.html
  - movies
    - main_content.html
    - texas
      - main_content.html

Edit the main_content.html files to edit the main content for the pages.  Be careful though - don't rename it and don't save invalid xhtml.  The point being that only a competant developer who knows this should be given webdav access.