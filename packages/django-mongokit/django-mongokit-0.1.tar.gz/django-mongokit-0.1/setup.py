#!/usr/bin/env python
# Copyright (c) 2010 Peter Bengtsson, peter@fry-it.com
from distutils.core import setup


setup(name='django-mongokit',
      version='0.1',
      author="Peter Bengtsson",
      author_email="peter@fry-it.com",
      url="http://github.com/peterbe/django-mongokit",
      description='Bridging Django to MongoDB with the MongoKit ODM',
      scripts=['bin/django-mongokit'],
      package_dir={'djangomongokitlib':'django-mongokitlib'},
      packages=['django_mongokit', 'django_mongokit.mongodb'],
      classifiers=['Development Status :: 3 - Alpha', # remember to change this one day to '5 - Production/Stable'
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities']
)
