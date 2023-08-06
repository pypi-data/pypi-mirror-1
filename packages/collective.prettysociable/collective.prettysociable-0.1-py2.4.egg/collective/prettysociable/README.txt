Introduction
============

prettySociable is a jQuery plugin that tries to make sharing fun while being easy to use. It was inspired by the sharing on mashable.com.

While ShareThis and AddThis provides a very useful piece code that allow users to share basically anything everywhere, their solution is not the prettiest nor the easiest to use. prettySociable simply asks the user to drag the items he wants to share onto the website he wants to send it to.

The code is fully customizable, either from the CSS, or through custom settings you can set upon initialization.

The original implementation can be found here: http://www.no-margin-for-errors.com/projects/prettysociable-mashable-like-sharing/

'collective.prettysociable' is an implementation of prettySociable for Plone.

The following sharing services are available (see configuration to disable services):

* Facebook

* Twitter

* Delicious

* Digg

* LinkedIn

* Reddit

* StumbleUpon

* tumblr


Installing
==========

This package requires Plone 3.x or later (tested on 3.3.3).

Installing without buildout
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install this package in either your system path packages or in the lib/python
directory of your Zope instance. You can do this using either easy_install or
via the setup.py script.

Installing with buildout
~~~~~~~~~~~~~~~~~~~~~~~~

If you are using `buildout`_ to manage your instance installing
collective.prettysociable is even simpler. You can install
collective.prettysociable by adding it to the eggs line for your instance::

    [instance]
    eggs = collective.prettysociable

After updating the configuration you need to run the ''bin/buildout'', which
will take care of updating your system.

.. _buildout: http://pypi.python.org/pypi/zc.buildout


Usage
=====

To use prettySociable for inline elements just add 'prettySociable' from the styles menu (Kupu and TinyMCE) to the link.


Configuration
=============

collective.prettysociable can be customized via property sheet (go to ZMI, portal_properties, prettysociable_properties).

* enable_default: Enable the default JS to render prettySociable-tagged links. Disable this option to add your own JS code (via JS in custom folder or in theme package). (default: True)

* enable_h1: If enabled a permalink will be added to every H1 (documentFirstHeading) and prettySociable activated for this link. (default: True)

* speed:

  * fast

  * normal (default)

  * slow

* opacity: value from 0.0 to 1.0 (default: 0.80)

* hide_flash: Hides all the flash object on a page, set to TRUE if flash appears over prettySociable (default: False)

* hover_padding: add extra padding to the link (default: 0)

* image_height: the height of the icon (in pixel, default: 70)

* image_width: the width of the icon (in pixel, default: 70)

* *_active: active the sharing for the service (default: True)

* *_encode: if sharing is not working, try to turn to false (default: True)

Copyright and Credits
=====================

prettysociable is developed by Stephane Caron (http://www.no-margin-for-errors.com) and is licensed under Creative Commons Attribution 2.5.

Author of collective.prettysociable: Thomas Massmann (thomas.massmann@inqbus.de).