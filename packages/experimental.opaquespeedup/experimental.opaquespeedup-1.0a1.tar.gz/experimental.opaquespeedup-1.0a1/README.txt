experimental.opaquespeedup
==========================

Introduction
------------

`experimental.opaquespeedup` is an approach to speed up event handling in
Plone 3.  Currently all events on content objects are getting dispatched to
so called "opaque" objects, which are sub-objects not handled by `OFS`'s
`ObjectManager` class.  Apart from the commenting framework such objects are
mostly unused nowadays.  However, for dispatching every single fired events
`CMFCatalogAware`'s rather expensive method `opaqueItems` is used in order to
collect all "opaque" objects for a given folderish object.  The method call
wakes up all objects in the folder and is completely uncached.  So the more
objects reside in a folder and the more event subscribers are being used by
the system, the slower things get.  And all events count.

This package tries to optimize things by replacing `opaqueItems` with a
version that'll query the catalog for contained "opaque" objects and cache
the results.  Initial tests indicate a significant performance improvement.

