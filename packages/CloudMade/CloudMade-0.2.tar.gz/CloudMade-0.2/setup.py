#!/usr/bin/env python

from distutils.core import setup

classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Web Environment
Intended Audience :: Developers
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Operating System :: OS Independent
Topic :: Software Development :: Libraries
Topic :: Scientific/Engineering :: GIS
"""

setup(
    name = "CloudMade",
    version = "0.2",
    description="CloudMade's online services client",
    long_description="""
CloudMade
=========

The CloudMade Python API is aimed at making access to CloudMade online services in Python easy.


Download and Installation
-------------------------

CloudMade can be installed with `Easy Install
<http://peak.telecommunity.com/DevCenter/EasyInstall>`_ by typing::

    > easy_install CloudMade

""",
    keywords='cloudmade geocoding routing tiles GIS',
    license='LGPL',
    author='Andrii V. Mishovskyi',
    author_email='amishkovskiy@cloudmade.com',
    url='http://developers.cloudmade.com/projects/show/python-lib',
    packages=['cloudmade'],
)
