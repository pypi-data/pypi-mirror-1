CSSManager: A Component of "WebLion CMS":http://weblion.psu.edu

Plone Versions

This product works for Plone 2.5, Plone 3+

Dependencies

  None
  
Description
    
    CSSManager is a simple add-on for managing CSS properties exposed by Plone 2 and 3. This tool
    can be used for quickly changing css values that are mapped to dtml-vars within plone. This is powerful for
    the person who doesn't know css or knows it very well and has a bunch of base_properties dtml-vars added to the base plone base_properties
    that map a theme of colors together. 
    
    CSSManager is a modified version of Michael Geddart's CSSManager, making it compatible with Plone 2.5 and later. 


Installation

    Installation works as usual: move CSSManager into your Products directory, restart Zope, and click site setup then "Add/Remove Products".

Use
    1.  You will see CSSManager listed under the heading "Add-on Product Configuration." 
        Follow the CSSManager link. To change the color of a CSS property, click the 
        palette icon next to the Value field. You can then use the slider to select a new color, or enter the hex code of a color. Click OK 
        when you are finished selecting a new color for a property. To change the logo, click upload file, and choose a new logo

    2.  Click "Save CSS" at the bottom of the main page when you are finished with your changes. 
       
    3.  The hope is you can use dtml-vars to your hearts content and match colors together that can be changed easily and fast

Multiple Property Sheets

    CSSManager can support editing of multiple property sheets in addition to base_properties.
    Add them by visiting the CSS tool in the ZMI.
    You'll need to have a property help template with the name "yourPropSheet_help.pt"
    to declare widgets and help texts. Model this on base_properties_help.pt.

Authorship

    * 0.5 and later by the WebLion Project Team(Rob Porter rhp110)

    * CSSManager's initial development was sponsored by Arche AG.
       "CSSManager":http://opensource.arche.de/products/cssmanager version 0.4.1 by "Michael Geddert":mailto:geddert@arche.de, "Arche AG":http://www.arche.de

Support
   
    * Please report bugs to the
      "WebLion issue tracker":https://weblion.psu.edu/trac/weblion/newticket.
   
    * Documentation: "WebLion wiki":http://weblion.psu.edu/trac/weblion
   
    * Contact us::
   
      WebLion Project Team
      Penn State University
      304 The 300 Building
      University Park, PA 16802
      webmaster@weblion.psu.edu
      814-863-4574
