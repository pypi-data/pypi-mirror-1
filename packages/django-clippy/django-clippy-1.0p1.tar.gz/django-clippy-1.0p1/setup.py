#!/usr/bin/env python
# encoding: utf-8
"""django-clippy provides a template tag for the Django Web Framework
to allow copying the Clipboard. 

Functionality is implemented in Flash.

Read more at http://github.com/mdornseif/django-clippy#readme
"""

# setup.py
# Created by Maximillian Dornseif on 2009-07-19 for HUDORA.
# Copyright (c) 2009 HUDORA. All rights reserved.


from distutils.core import setup
setup(name='django-clippy',
      maintainer='Maximillian Dornseif',
      maintainer_email='md@hudora.de',
      version='1.0p1',
      url='http://github.com/mdornseif/django-clippy#readme',
      description='Flash based template tag for Django to allow copying the clipboard',
      long_description=__doc__,
      classifiers=['License :: OSI Approved :: BSD License',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python'],
      packages=['clippy', 'clippy.templatetags'],
      # I simply don't understand how to make distutils do my bidding
      #data_files=[('clippy', ['static/clippy.swf', 'templates/clippy/demo.html'])],
      #package_data={'clippy': ['static/clippy.swf', 'templates/clippy/demo.html']},
      install_requires=['Django'],
)
