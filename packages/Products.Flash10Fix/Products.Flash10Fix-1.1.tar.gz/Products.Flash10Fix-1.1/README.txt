Introduction
============

Adobe Flash 10 introduced an additional security check such that it will only
play files served with the "Content-Disposition: inline" header.  Current
versions of Plone do not set this header correctly for .swf files stored
as ATFiles.  (See http://dev.plone.org/plone/ticket/8624 for more information.)

This package corrects that by augmenting ATFile's list of mimetypes that
should be served with the inline content disposition.

This patch is no longer necessary in Plone 3.2.x

Note: This patch does not help with .swf files served by ATFlashMovie in Plone
3.  To make those work, make sure you have ATFlashMovie 1.0.3.


Installation
------------

This product has been tested in Plone 2.5 and Plone 3.x

If using buildout, simply add Products.Flash10Fix to your buildout's list of
eggs, rerun buildout, and restart Zope.

If not using buildout, unpack the product tarball in your Products directory
and restart Zope.

No additional steps are required.  If the patch was successful, you should
see "Flash10Fix Patched the following classes: ATFile" on the console when
running Zope in the foreground.

Credits
-------

Thanks to James Nelson for the report and preliminary patch.
