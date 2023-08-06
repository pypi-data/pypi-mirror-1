===========
PyConBrasil
===========

This software was writen to manage the papers and registration for
PyConBrasil, the Brazilian Python Conference.

It doesn't means, though, that you can't use it to manage you're own
conference! :o)

The motivation to start this product came from the insistency of Erico
Andrei, in the first preparation meeting for the II PyConBrasil (2006),
where he stated that we should do it in Python and make it available
to everyone who did the registration in the event.

And he was right about it... ;-)


Dependencies
------------

  - Plone 3.1.x - http://plone.org/products/plone


Installation
------------

Buildout-way::

  - Edit your buildout.cfg file, so that::

      [buildout]
      ...
      eggs =
          ...
          Products.PyConBrasil

      [instance]
      ...
      zcml =
          ...
          Products.PyConBrasil

  - Restart Zope

  - In the ZMI, go to your Plone instance, and install the product using
    the portal_quickinstaller tool

Authors
-------

  - Jean Rodrigo Ferri - jeanrodrigoferri at yahoo dot com dot br

  - Dorneles Tremea - dorneles at x3ng dot com dot br
  
  - Erico Andrei - erico at simplesconsultoria dot com dot br


Contributors
------------

  - Fabiano Weimar - xiru at xiru dot org

  - Rodrigo Senra - rsenra at acm dot org


Copyright
---------

APyB - Associacao Python Brasil: http://associacao.pythonbrasil.org
