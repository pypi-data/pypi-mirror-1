Introduction
============

A two-column theme for Plone 3 based on Andreas02 by Andreas Viklund: http://www.oswd.org/design/preview/id/2204.

Theme developed by David Little david@littled.net.

This is completely CSS based and theme has its own main_template in skins/plonetheme_simplicity_templates. The main_template and associated CSS and Javascripts have been copied from the Plone Tableless theme by Simon Kaeser: http://plone.org/products/plone-tableless.

Installation
============

The easiest way to install Andreas02 is via buildout:

In your buildout file, include the following lines:

Under the eggs = section in your buildout file (e.g. buildout.cfg), add plonetheme.andreas02, i.e.

[buildout]
eggs =
    plonetheme.andreas02

In the same file under [instance] (or [clientx] if using Zeo), add plonetheme.andreas02 i.e.

zcml =
   plonetheme.andreas02

and re-run buildout. This will download and install Andreas02 for you. You can then install this into your Plone site using "Add-on Products" (or "Add / remove products" depending on which version of Plone 3 you are using) via your site's "Site's setup" link (usually in the top right hand corner of your site). You can also install via the ZMI using the portal_quickinstaller or via portal_setup.

For full installation instructions, see docs/INSTALL.txt.

Customising
===========

BANNER

You can replace the theme's "splash" image banner by uploading your own to the root of your Plone site or placing it in the portal_skins/custom directory of your site in the ZMI. The banner should be called "banner.jpg" and be 760 pixels (width) by 200 pixels (height). The image is displayed as a background image and some cropping will occur.

CSS

The main CSS file for Andreas02 is located in portal_skins/plonetheme_andreas02_styles/andreas02.css. You can customise this into your site's portal_skins/custom directory via the ZMI. The associated Internet Explorer fixes CSS file is also in plonetheme_andreas02_styles and is called IEFixes.css
