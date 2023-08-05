What is MinificationWebHelpers?
===============================

Consider the MinificationWebHelpers_ as an extension to WebHelpers_.

Basicly it adds two more options to the WebHelpers_ javascript_include_tag_
and stylesheet_link_tag_ functions:

* **minified**: Minifies, ie, reduces as much as possible each of the files
  passed to it's minimum size to reduce page load times.
* **combined**: Joins all files passed into a single one to reduce server
  requests which in turn reduces page load times.


For an up-to-date read of the documentation, please `read the documentation
page on site`__.

Usage
-----

On your own Pylons_ application, inside ``<app>/lib/helpers.py`` you add:

.. sourcecode:: python

  from minwebhelpers import *


Then, inside a template you could have:

.. sourcecode:: html+genshi

  <head>
    ${ h.javascript_include_tag('/js/file1.js', '/js/file2.js',
                                minified=True, combined=True )}
  </head>

The above would mean ``file1.js`` and ``file2.js`` would be combined and then
minimized.

Instalation
-----------

It's as easy as::

  sudo easy_install MinificationWebHelpers


Or if you wish to install current trunk::

  sudo easy_install http://pastie.ufsoft.org/svn/sandbox/MinificationWebHelpers/trunk


.. _MinificationWebHelpers: http://pastie.ufsoft.org/wiki/MinificationWebHelpers
.. _WebHelpers: http://pylonshq.com/WebHelpers/module-index.html
.. _javascript_include_tag: http://pylonshq.com/WebHelpers/module-webhelpers.rails.asset_tag.html#javascript_include_tag
.. _stylesheet_link_tag: http://pylonshq.com/WebHelpers/module-webhelpers.rails.asset_tag.html#stylesheet_link_tag
.. _Pylons: http://pylonshq.com
.. __: http://pastie.ufsoft.org/wiki/MinificationWebHelpers
