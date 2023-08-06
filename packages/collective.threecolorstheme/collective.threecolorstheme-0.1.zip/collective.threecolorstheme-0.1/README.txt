...::contents

I. Introduction
===============

A collective phantasy dynamic theme.
Based on three colors.

II. Installation
================

Read docs/INSTALL.txt to install this package in your zope instance
using buildout or easy_install (read it carefully ! there's an overrides 
section)

In your Plone site > ZMI > portal_quickinstaller

Choose "Three Colors Theme" product, and click on Install
This will install the plone product and all dependencies
(collective.phantasy and SmartColorWidget)

III. Usage
==========

1. Change skin for the portal :
-------------------------------

  - Go to your plone site > dynamic-root-skin
  
  - click on edit
  
  - change the 3 colors, 
  
  - change the dimensions and other fields values
  
  - set filenames for some fields
  
  - load your custom css or images inside the skin 
    using "Import Files" form (post a zip with all your files)
    or using PloneFlashUpload (a powerful Plone product)
    
  - take care of filenames inside the skin 
    (they must be the same as names inside the skin edit form, perhaps you will need to change 
    the values because Plone has changed them for valid ids).
  
2. change a skin for a folder :
-------------------------------

  - Go to your plone site > folder-skins-repository
  
  - Add a new phantasy skin inside the skins repository
  
  - In this new skin you will get the same values as set in dynamic-root-skin
  
  - Change it (do the same thing as you've done in $1)
  
  - Go to any folder on your site for which you want another skin
  
  - Click on "edit" tab
  
  - A "phantasy-skin" field is available
    so you can browse the portal to choose another skin for your folder.
    
  - Note that the folder get the two css (from the root skin and from the folder skin)  
  

3. Create a new skin with Samples provided in this product
----------------------------------------------------------

  - Add a new dynamic skin (see $1 & $2)
  
  - Click on import images and files
  
  - Inside the folder alternate_skin, choose the archive alternate_skin.zip click on Import
  
  - Read howtouseit.txt (to set values according to new images)
  
  - There is another example inside ornicart_skin Folder


   

