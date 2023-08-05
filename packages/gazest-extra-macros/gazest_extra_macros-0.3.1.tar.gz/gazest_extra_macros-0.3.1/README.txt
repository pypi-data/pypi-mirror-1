
Gazest Extra Macros
===================


About
-----

This package provides additional macros to the markup of the Gazest
Wiki.  You only have to install it; setuptools will take care of the
rest.  

In a not too distant future, this package might even provide useful
markup but at the moment it's just an example to show how a Gazest
site admin can augment his markup.


Installation
------------

Install using easy_install:

  $ easy_install gazest_extra_macros


Install using setup.py

  $ tar -xvf gazest_extra_macros-X.Y.Z.tar.gz
  $ cd gazest_extra_macros-X.Y.Z
  $ su
  # python setup.py install


Usage
-----

Once the package is installed, edit a wiki page to look like:

  I {{echo.twice really}} like {{math.log 2.0138}} because it's such
  a sexy waist to hip ratio.

There is absolutly no doc, just look at the sources.  All the function
are simple enough to be understood with an eye glance.


About Asciidoc
--------------

The Asciidoc renderer requires an experimental branch of Asciidoc
available here:

   http://ygingras.net/files/asciidoc-8.3.5dev.tar.gz
