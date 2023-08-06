===========
Dolmen Site
===========

:Test-Layer: functional

Dolmen is a simple application. The package `dolmen.app.site` provides
an easy way to bootstrap your own applications. It exposes two elements,
the Dolmen object and the IDolmen interface.

This creation of Dolmen Application is straightforward::

    >>> import grok
    >>> from zope.event import notify
    >>> from dolmen.app.site import Dolmen, IDolmen

    >>> root = getRootFolder()
    >>> rocks = Dolmen()
    >>> notify(grok.ObjectCreatedEvent(rocks))
    >>> root['rocks'] = rocks

    >>> root.get('rocks').__class__.__name__
    'Dolmen'

    >>> rocks.title
    u'My Dolmen Site'

    >>> IDolmen.providedBy(rocks)
    True

    >>> rocks.getSiteManager()
    <LocalSiteManager ++etc++site>


Dolmen is a `dolmen.content` Container (read `dolmen.content`)
documentation for more information::

    >>> from dolmen.content import IBaseContent, IContainer
    >>> IBaseContent.providedBy(rocks)
    True
    >>> IContainer.providedBy(rocks)
    True
