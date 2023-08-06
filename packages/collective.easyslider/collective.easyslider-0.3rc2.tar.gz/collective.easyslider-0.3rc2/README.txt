Introduction
============
This product allows you to easily add an easySlider content rotator to any page on a plone site.

How-to
------
On a page, click actions -> Add Slider.  It should bring you to a slider settings page where you can modify different aspects of the slider.  Keep in mind that the slides are fixed width so you need to specify the size you want.  Then you'll want to start adding your slides.  To do this just click ``add new slide`` near the bottom of the page.  Once you've finished adding slides and re-ordering slides, click ``save`` and you should see the slider on your page now.

You can also select a slider view for Folder and Collection content types.  Then the slider settings for that page will include settings to limit the amount of slides to have and to limit the type of slides used.

Demo
----
A demo of a site using this product can be found at ``http://www.nathanvangheem.com/``

Installation
------------
* add collective.easyslider to your eggs and zcml sections
* re-run buildout
* install the product like you would any other Plone product

Uninstall
---------
* Uninstall like normal
* go to portal_setup in the zmi, click the 'import' tab, select "collective.easyslider uninstall" and click the "Import all steps" button at the bottom to perform clean up.

Credits and Contributions
-------------------------
* a lot of the credit for the inspiration, styling and insight into this product belongs to Espen Moe-Nilssen 
