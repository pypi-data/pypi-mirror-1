# -*- coding: utf-8 -*-
from distutils.core import setup
import os



# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('django_addons'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[14:]
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(name='django-addons',
      version="0.2",
      description='Addon framework for Django',
      author='Lauri Võsandi',
      author_email='lauri@indifex.com',
      url='http://www.bitbucket.org/indifex/django-addons/wiki/',
      download_url='http://bitbucket.org/indifex/django-addons/get/tip.gz',
      package_dir={'django_addons': 'django_addons'},
      packages=packages,
      package_data={'django_addons': data_files},
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      )
