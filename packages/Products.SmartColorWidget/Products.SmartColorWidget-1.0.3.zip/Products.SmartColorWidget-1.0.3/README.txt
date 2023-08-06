ABOUT THIS PRODUCT
==================

**SmartColorWidget is a user-friendly color picker widget for Archetypes.**
It allow quick and easy color selection from 3 different ways:

* HTML color value
* Color table and lightness bar slider
* Hue/Lightness/Saturation fields

The 3 inputs modes are javascript-wired and dynamically change when
anything is modified

A demo type is included. Set INSTALL_DEMO_TYPES = 1 in config.py to
enable it.

DEPENDENCIES
============

* Plone 3.1+ (or Plone3.0.x with jquery.js already installed)

Note : 

* jquery.js must be installed in portal_javascripts to make this SmartColorWidget version working. 

* with Plone 3.1 and more, jquery is already installed by default.

Installation
============

  1. read docs/Install to install the package in your zope instance
     using buildout or easy_install

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

This product was built by:

Pierre Gayvallet "support@ingeniweb.com":mailto:support@ingeniweb.com

   "http://www.ingeniweb.com":http://www.ingeniweb.com


Thanks
======

The jQuery team, for their powerfull javascript library
    "http://jquery.com":http://jquery.com

EasyRGB, for the colors transformation formulas
    "http://www.easyrgb.com":http://www.easyrgb.com

Roland Fasching "rof@sterngasse.at":mailto:rof@sterngasse.at for the widget idea from ATColorPickerWidget
   "http://www.sterngasse.at":http://www.sterngasse.at
   
   

