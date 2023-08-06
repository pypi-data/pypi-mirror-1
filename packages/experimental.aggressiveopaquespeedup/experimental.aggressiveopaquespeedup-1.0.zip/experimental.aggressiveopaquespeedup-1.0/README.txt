Introduction
============

This path improve overall performance of Plone. It remove opaqueitems feature 
from CMF (just keep talkback support)

I have discover this issue by profiling just a simple javascript file fetch
throw Plone document html page and discuss it throw CMF mailing list:
http://mail.zope.org/pipermail/zope-cmf/2009-August/028559.html

The result is 25% better on the total time spend in the request. Becarefull if 
you use a third part product that use opaqueitems and make me know if you it is,
I will add it to this page. At the moment only talkback use it and are supported.