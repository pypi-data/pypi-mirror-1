Introduction
============

ImageScales applies a simple patch to the schema used for ATImage
to allow specification of image scales on a site-by-site basis. It
should work with Plone 2.5 and 3.x. For Plone 3.x, you may wish to
use plone.app.imaging instead.

Installation
============

Install ImageScales by adding "Products.ImageScales" to your buildout
eggs list.

It's also possible to extract the "ImageScales" directory in 
ImageScales/Products and putting it in an old-style Zope Products
directory.

ImageScales will not show up in your Plone add/remove products configlet
as it needs no special installation.

How it works
============

Once the ImageScales patch is in place, getAvailableSizes method calls
will be routed through a method installed on startup. This method will
look for a portal_properties property sheet named imaging_properties.
If it finds it, it will read the lines property allowed_sizes to get a list of
sizes. If either the special property sheet or property are not found,
the original ATImage scales will be used.


Configuring Site Scales
=======================

Create in portal_properties a plone property sheet named imaging_properties.
Create in that property sheet a lines property with the id "allowed_sizes".

Sizes should contain a list of lines. Each line is a scale specification. Each
specification should have the format::

    id horizontal_pixels:vertical_pixels
 
For example, to recreate the standard ATImage scales, the property would read::

    large 768:768
    preview 400:400
    mini 200:200
    thumb 128:128
    tile 64:64
    icon 32:32
    listing 16:16
 
If you're using ImageScales with a theme product that has a GS profile, you can
create the property sheet with a property_tools.xml specification like::

    <?xml version="1.0"?>
    <object name="portal_properties" meta_type="Plone Properties Tool">
     <object name="imaging_properties" meta_type="Plone Property Sheet">
      <property name="title">Image Scales for ATImage</property>
      <property name="allowed_sizes" type="lines">
       <element value="large 768:768"/>
       <element value="preview 400:400"/>
       <element value="mini 200:200"/>
       <element value="thumb 128:128"/>
       <element value="tile 64:64"/>
       <element value="icon 32:32"/>
       <element value="listing 16:16"/>
      </property>
     </object>
    </object>

However you build your property sheet, you'll need to use the portal_atct tool
to rebuild image scales in existing images any time you make a change.
