Introduction
============

Used in production in http://www.v2.nl/

This product has a dependency on collective.contentLeadImage and collective.flowplayer. So these products must be installed along with v2.theme.

Configuration
=============

To customize the theme by changing colors, fonts and images (like the logo for example) you only need to: 

- log in as an administrator to your plone instance;

- Navigate to 'site setup'->'ZMI (Zope Management Interface)' or append '/manage' to your site's URL;

- Click on 'portal_skins (Controls skin behaviour (search order etc))';

- There are three customizable skin layers: v2_theme_custom_images, v2_theme_custom_templates and v2_theme_styles;

- To customize any of the files within these layers you can click on them and then press the customize button.
 
To change colors and fonts:

- Inside v2_theme_styles click on the file 'base_properties (V2 Theme's color, font, logo and border defaults)'. This file controls most of the visual apearence of the site;

- Click customize;

- Configure this file at will. The most important properties would be 'globalStrongColor' that controls the main color of the theme  (defaults to strong green) and
  'contentViewBackgroundColor' that controls the background color of the interface tabs and other small elements of the theme (defaults to light green); 
  note: IT IS NOT RECOMENDED TO CHANGE THE FILENAMES ON THIS FILE (images). Instead, customize the images on the v2_theme_custom_images layer with your own (see below how to do this).

To customize images (Example of the logo):

- Inside v2_theme_custom_images choose the image you want to customize, ex. logo.png;

- Click the customize button.

- Choose the file you want to be on it's place. You can use a transparent PNG (recommended) so that the image does not go over the shadou of the header of the site.
  The default logo uses a non-transparent PNG to cover that shadow with a new one that wraps arround the letters. Use your creativity to override this as you wish.

- You can override all the images of the theme with this method.

 - Tip: The background of the website is the file 'bg_image_250.jpg' (if you do not wish to have a background you can set the property 'animation' to 'none' in 'v2_theme_styles -> base_properties')

 - Tip: The background of the blocks and the page body text wrapper is the file backOpacityIE and is a semitransparent PNG image.

 - Tip: The background of the event date display in the blocks and event view are images and they are separated in future events and past events so you can give a different background to each of them

 - Tip: To change the FAVICON customize the image favicon.ico in v2_custom_images (attention, it has to be an .ico file, to create one from an image you can use an .ico generator like http://tools.dynamicdrive.com/favicon/ )
