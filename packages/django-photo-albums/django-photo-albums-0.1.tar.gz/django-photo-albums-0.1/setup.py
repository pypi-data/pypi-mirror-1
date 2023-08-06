#!/usr/bin/env python
from setuptools import setup

setup(
      name='django-photo-albums',
      version='0.1',
      author='Mikhail Korobov',
      author_email='kmike84@gmail.com',
      url='http://bitbucket.org/kmike/django-photo-albums/',      
      
      description = 'Pluggable Django image gallery app.',
      license = 'MIT license',
      packages=['photo_albums'],
      requires = ['django (>=1.1)'],
      install_requires=['django-generic-images >= 0.12', 'django-annoying > 0.5'],
      
      classifiers=(
          'Development Status :: 3 - Alpha',
          'Environment :: Plugins',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Natural Language :: Russian',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules'
        ),
)