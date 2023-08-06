#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='django-pagehelp',
      version='1.0',
      description="A Django application which provides contextual help for "
        "your site's pages.",
      author='Chris Beaven',
      author_email='smileychris@gmail.com',
      url='http://bitbucket.org/smileychris/django-pagehelp/',
      packages=find_packages(),
      package_data={'pagehelp': ['templates/*.*', 'media/*.*']},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Framework :: Django',
      ],
)
