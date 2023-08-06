Table of Contents
-----------------

  1. Overview
  2. Authors & Contributors
  3. Dependencies
  4. Installation
  5. Customization
  6. Support

1. Overview
-----------

"Keep it simple" is a fluid 3-column theme, minimalistic and light colored
design. The original web template comes from http://www.styleshout.com.

The implementation permited different font sizes whit a great degree of
adaptation.


2. Authors & Contributors
-------------------------

* Silvestre Marcelo Huens (Quimera)(www.menttes.com)
  Ported template to Plone 3.x.
* http://www.styleshout.com
  Created the original web template.


3. Dependencies
---------------

The following are required to use this theme:

* Zope
* Plone 3.x
* SetupTools


4. Installation
---------------

Assuming that you are using zc.buildout and the plone.recipe.zope2instance
recipe to manage your project, proceed this way:

* Add plonetheme.keepitsimple to the list of eggs to install, e.g.:

::

  [buildout]
   ...
   eggs =
       ...
       plonetheme.keepitsimple

* Re-run buildout, e.g. with:

::

  $ ./bin/buildout


Then you can install the product into your Plone site from the Plone control
panel.

In Plone 4, if you uninstall plonetheme.keepitsimple you will notice that the
site will start looking very raw in style. This is because 'Plone Default' is
set as default skin after uninstallation. To change the default skin you need
to go to the Themes tool in the control panel and select a default skin
different from 'Plone Default'.


5. Customization
----------------

This theme have a banner with image and text, there you can customize:

* Logo: place a logo.jpg file in the folder skins/plonetheme_keepitsimple_custom_images
* Text: edit the template intro_text.pt in the folder browser/templates

Customization done by this product:

* The main_template was customized for change the order of the columns.
* A viewlet manager and viewlet was added in the header to manage the logo and
  text banner.
* The search box in the top was customized (no more "current folder only" check
  box)


6. Support
----------

   For support with this theme, you can contact a Plone person,
   the Plone mailing lists, or ask for help in the Plone IRC
   channel (#plone).
