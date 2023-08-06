#!/usr/bin/env python
 
from distutils.core import setup

# In distutils, "packages" needs to have *all* directories with files in them
# or the missing files won't be installed. This code nicked from django.

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

home_dir = 'RelayMuseum'
packages = []

import os

# Assure we're in the right place
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

# Recursively build lists of files
for dirpath, dirnames, filenames in os.walk(home_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))

README_FILE = open('README.rst')
try:
    long_description = README_FILE.read()
finally:
    README_FILE.close()
 
setup(name='RelayMuseum',
        version='0.1.0',
        packages=packages,
        package_data={'RelayMuseum': ['templates/*', 'media/css/*', 'media/img/*']},
        data_files = ('README.rst', 'INSTALL.rst', 'requirements.txt'),
        platforms=['any'],
        description='A web-museum for conlang-relays.',
        author_email='kaleissin@gmail.com',
        author='kaleissin',
        long_description=long_description,
        download_url='http://github.com/kaleissin/RelayMuseum.git',
        classifiers=[
                'Development Status :: 4 - Beta',
                'Environment :: Web Environment',
                'Framework :: Django',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: MIT License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Libraries :: Application Frameworks',
                'Topic :: Software Development :: Libraries :: Python Modules',
        ]
)
