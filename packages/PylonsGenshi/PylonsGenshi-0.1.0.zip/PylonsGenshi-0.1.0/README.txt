What is PylonsGenshi?
=====================

PylonsGenshi is a paster_ template based on the Pylons_ one but addressing
Genshi_ as it's templating engine.

It basicly provides Markup_ wrapped webhelpers and a Formencode_ validate
decorator designed to work with Genshi_.

For an up-to-date read of the documentation, please `Read the Documentation
page on site`__.


Instalation
-----------

It's as easy as::

  sudo easy_install PylonsGenshi


Or if you wish to install current trunk::

  sudo easy_install http://pastie.ufsoft.org/svn/sandbox/PylonsGenshi/trunk


PylonsGenshi can optionally install the MinificationWebHelpers_ which would
already be wrapped in Markup_ objects. To install that extra::

  sudo easy_install PylonsGenshi[minification]


.. _paster: http://pythonpaste.org/script/developer.html#templates
.. _Pylons: http://pylonshq.com
.. _Genshi: http://genshi.edgewall.org
.. _Markup:
  http://genshi.edgewall.org/wiki/ApiDocs/0.4.x/genshi.core#genshi.core:Markup
.. _Formencode: http://www.formencode.org/
.. __: http://pastie.ufsoft.org/wiki/PylonsGenshi
.. _MinificationWebHelpers: http://pastie.ufsoft.org/wiki/MinificationWebHelpers
