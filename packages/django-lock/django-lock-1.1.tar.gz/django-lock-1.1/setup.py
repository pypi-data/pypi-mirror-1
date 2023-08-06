#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='django-lock',
      version='1.1',
      description='A protection method for Django views or complete sites.',
      author='Chris Beaven',
      author_email='smileychris@gmail.com',
      url='http://code.google.com/p/django-lock/',
      packages=find_packages(),
      include_package_data=True,
     )
