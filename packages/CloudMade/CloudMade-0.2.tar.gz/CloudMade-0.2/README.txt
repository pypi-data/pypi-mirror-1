=========
CloudMade
=========

CloudMade is a python API for CloudMade's online services: Geocoding, Routing and Tiles.

Full documentation is available online at http://developers.cloudmade.com/documentation/python-lib/

------------
Installation
------------

Using easy_install

    easy_install CloudMade

If you want to install from source you can run the following command:

    python setup.py install

Testing
=======

To test the source distribution you will need to install CloudMade and nose.


    easy_install py

Once the required packages are installed you can run the tests with the 
following command in the root of the source tree:

    py.test

Module Documentation
====================

To generate module documentation you will need to install epydoc the issue the following commands:

    easy_install sphinx

Then to build the documentation issue following command in the docs/ directory:

    make html

This will build documentation in docs/_build/ directory. For more information
on building documentation from source, visit official `Sphinx site <http://sphinx.pocoo.org/>`_\.
