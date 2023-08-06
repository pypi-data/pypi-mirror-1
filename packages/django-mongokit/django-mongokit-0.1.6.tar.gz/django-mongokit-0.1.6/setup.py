#!/usr/bin/env python
# Copyright (c) 2010 Peter Bengtsson, peter@fry-it.com
from distutils.core import setup
#from pkg_resources import resource_string



setup(name='django-mongokit',
      version=open('django_mongokit/version.txt').read(),#resource_string(__name__, 'django_mongokit/version.txt'),
      author="Peter Bengtsson",
      author_email="peter@fry-it.com",
      url="http://github.com/peterbe/django-mongokit",
      description='Bridging Django to MongoDB with the MongoKit ODM',
      long_description=open('README.md').read(),#resource_string(__name__, 'README.md'),
      package_dir={'djangomongokitlib':'django-mongokitlib'},
      packages=['django_mongokit', 'django_mongokit.mongodb'],
      package_data={'django_mongokit':['version.txt']},
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities']
)
