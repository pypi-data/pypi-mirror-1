*******************************
Download recipe for Selenium RC
*******************************

This package downloads and installs Selenium RC using zc.buildout. It is based
on hexagonit.recipe.download.

buildout.cfg Example::

  [buildout]
  parts=seleniumrc

  [seleniumrc]
  recipe=collective.recipe.seleniumrc

A control script will be created based on the part name. In this case a
control script will be created in bin/seleniumrc

You may also be interested in the selenium module for Python which allows you
to control Selenium RC.

AUTHOR
------

Jordan Baker <jbb@scryent.com>

LICENSED
--------

Open Source License - Zope Public License v2.1

See doc/LICENSE.txt

