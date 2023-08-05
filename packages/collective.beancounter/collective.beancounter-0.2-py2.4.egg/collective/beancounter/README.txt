collective.beancounter
======================

:Author:    $Author: seletz $
:Date:      $Date: 2007-10-18 22:32:30 +0200 (Thu, 18 Oct 2007) $
:Revision:  $Revision: 52040 $

Abstract
--------

This package scratches an itch of mine in providing a very simple viewlet
which displays the percentage a content is filled by an user.

setup stuff
------------

::

    >>> class Mock(object):
    ...    def __init__(self, **kw): self.__sict__.update(kw)

Blurb
-----

First we define an interface to be used to mark bean-countable content::

    >>> from zope import interface
    >>> class IBeanContable(interface.Interface):
    ...     """ a content which is bean countable """

The counting itself is very simple and done by an adapter. We simply count
which fields in the **default** schemata are filled. We there count only
the writable fields. From that we calculate a percentage.

Lets define a interface for that functionality::

    >>> class IBeanCounter(interface.Interface):
    ...     percentage = interface.Attribute(u"The percentage filled")

Now lets create some content class to test our stuff::

    >>> _ = self.folder.invokeFactory("Document", "doc")
    >>> doc = self.folder.get(_)

Count the fields which are in the **default** schemata and are rewd/write::

    >>> len([f for f in doc.Schema().fields() if f.schemata=="default" and f.mode =="rw"])
    4

Ok, now how many of them are filled?::

    >>> l = [f for f in doc.Schema().fields() if f.schemata=="default" and f.mode =="rw"]
    >>> [f.getName() for f in l if f.get(doc)]
    ['id']

Ok, fair enough. Now lets do the opposite::

    >>> [f.getName() for f in l if not f.get(doc)]
    ['title', 'description', 'text']

Ok, thats enough. Lets wrap it up.

Implementation
--------------

We have an adapter::

    >>> from collective.beancounter.adapter import ATBeanCounter
    >>> ct = ATBeanCounter(doc)
    >>> print ct.percentage
    25.0

Fill out completely::

    >>> doc.update( title="muha", text="haha", description="desc")
    >>> ct = ATBeanCounter(doc)
    >>> print ct.percentage
    100.0

Yay.



::

 vim: set ft=rst tw=75 nocin nosi ai sw=4 ts=4 expandtab:
