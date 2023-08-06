Plone Flash Upload
==================

Plone Flash Upload is a Plone add-on product which adds an upload tab to
folders which takes the user to an upload form.  This upload form uses a flash
applet to provide the ability to upload multiple files simultaneously.

Requirements
------------

The 1.1 version only works on plone 3.0. Also you'll apparently need zope
2.10.5 as otherwise lib/python packaged can't be in the Products namespace.

* Zope 2.10.5+
* Plone 3.0.x

Installation
------------

Option one: use buildout and specify 'Products.PloneFlashUpload' as an egg
dependency. (Or depend on it in your own product's setup.py).

Option two: simply extract downloaded archive into the
``$INSTANCE_HOME/lib/python`` directory and (re)start Zope.

Once Zope is running, go to the Plone site's *Add/Remove Products*
configuration screen and install the *PloneFlashUpload* product.

Basic Usage
-----------

After installation of the product is complete, go to any folder within the
plone site and a new *upload* tab should be present if the current user has
access to add new files to the folder.

Additional Notes
----------------

- The flash applet has been tested (and runs successfully) on MSIE6, MSIE7,
  Firefox 1.5 (WinXP), Firefox 2.0 (WinXP/Linux) and various Safari and
  Firefox versions on MacOSX.  If a particular browser is found not to work,
  please submit an issue to the issue tracker.

- Any file that is uploaded will try to use the content type registry to
  determine what portal type should be the result of the file being uploaded
  (ie jpg's created as Image's and random binary files created as File's).  It
  should be observed though that only portal types defined within the PFU
  configlet are possible candidates (ie add more here if you have additional
  custom types you are using and have registered with CTR).

Issue Tracker, SVN, Other Resources
-----------------------------------

Project Homepage
  http://www.plone4artists.org/products/ploneflashupload

Issue Tracker
  http://www.plone4artists.org/products/ploneflashupload/ploneflashupload-issues

Source Control Repository
  http://svn.plone.org/svn/collective/PloneFlashUpload

Testing
-------

To run the Plone Flash Upload tests you must use the standard Zope testrunner::

  $INSTANCE_HOME/bin/zopectl test -s Products.PloneFlashUpload

License
-------

This product and it's contents are covered under the Zope Public License
(ZPL).  More information can be found in ``LICENSE.txt``.

Credits and Copyrights
----------------------

This product was created by Rocky Burt (rocky AT serverzen.com) on behalf of
4teamwork (http://4teamwork.ch) and Jazkarta (http://www.jazkarta.com).

Extra kudos to the author(s) of ``z3c.widget.flashupload`` which
PloneFlashUpload uses as the source of the actual flash applet.

`Reinout van Rees <mailto:reinout@zestsoftware.nl>`_ has updated the product
for plone 3.0 and turned it into an egg for `Zest software
<http://zestsoftware.nl/>`_.