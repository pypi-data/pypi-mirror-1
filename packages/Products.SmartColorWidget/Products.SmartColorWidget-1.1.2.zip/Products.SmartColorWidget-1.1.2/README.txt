================
SmartColorWidget
================

**SmartColorWidget is a user-friendly color picker widget for Archetypes.** It
allow quick and easy color selection from 3 different ways:

* HTML color value
* Color table and lightness bar slider
* Hue/Lightness/Saturation fields

The 3 inputs modes are javascript-wired and dynamically change when anything is
modified

A demo type is included. Set `INSTALL_DEMO_TYPES`` = 1 in ``config.py``` to
enable it.

Requirements
============

* Plone 3.1+,

* Plone 3.0 users must add ``collective.js.jquery`` to the eggs list in their
  ``buildout.cfg``.


Installation
============

1. read docs/Install to install the package in your zope instance using buildout
   or easy_install

2. Install the skin in your Plone Site with the Quickinstaller tool

Usage
=====

* In your custom Archetype, add::

    from Products.SmartColorWidget.Widget import SmartColorWidget


*  Use it like a regular field/widget in your Type's Schema.
   Example::

     StringField('color',
                 default='#00FFFF',
                 searchable=0,
                 required=0,
                 widget=SmartColorWidget(
                     label='Color',
                     )
                ),

Credits
=======

This product was built by `Pierre Gayvallet <mailto:support@ingeniweb.com>`_.

Thanks
======

The `jQuery team <http://jquery.com>`_, for their powerfull javascript library.

`EasyRGB <http://www.easyrgb.com>`_, for the colors transformation formulas.

`Roland Fasching <http://www.sterngasse.at>`_ for the widget idea from
ATColorPickerWidget.
