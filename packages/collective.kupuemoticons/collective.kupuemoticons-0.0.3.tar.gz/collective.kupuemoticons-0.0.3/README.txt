Introduction
============

A tool to enable animated emoticons for KUPU.


FEATURES
--------

- 18 different animated emoticons
- inserts the image into KUPU, not a ":-)" or ":)"
- adds only one button to the KUPU toolbar where you can access the complete
  emoticon-set over a KUPU panel.


INSTALL
-------

Add this to your buildout.cfg::

    eggs =
        ${buildout:eggs}
        ${plone:eggs}
        collective.kupuemoticons

    zcml =
        collective.kupuemoticons

install it with the quickinstaller.

**This version is tested with Plone 3.0.6 and Plone 3.1.5.1**


WARNING
-------

This package overwrites kupu_wysiwyg_support.html to add the new toolbar
button and drawer to KUPU.


NOTE
----

we are no KUPU core developers, so maybe there is a simpler way to do that.
Feedback is more than welcome...

::
 vim: set ft=rst ts=4 sw=4 expandtab tw=78 :
