# -*- coding: utf-8 -*-
from codecs import BOM
import os
from setuptools import setup, find_packages
from django_addons import get_version

readme_file = open(u'README')
long_description = readme_file.read()
readme_file.close()
if long_description.startswith(BOM):
    long_description = long_description.lstrip(BOM)
long_description = long_description.decode('utf-8')


setup(name='django-addons',
      version=get_version().replace(' ', '-'),
      description='Addon framework for Django',
      long_description=long_description,
      author='Lauri Võsandi',
      author_email='lauri@indifex.com',
      url='http://www.bitbucket.org/indifex/django-addons/wiki/',
      download_url='http://bitbucket.org/indifex/django-addons/get/tip.gz',
      zip_safe = False,
      packages=find_packages(),
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
)
