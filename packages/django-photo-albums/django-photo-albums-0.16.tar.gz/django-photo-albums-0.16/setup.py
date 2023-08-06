#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup


setup(
      name='django-photo-albums',
      version='0.16',
      author='Mikhail Korobov',
      author_email='kmike84@gmail.com',
      url='http://bitbucket.org/kmike/django-photo-albums/',      
      
      description = 'Pluggable Django image gallery app.',
      license = 'MIT license',
      packages=['photo_albums'],
      requires = ['django (>=1.1)'],
      install_requires=['django-generic-images >= 0.29', 'django-annoying > 0.7'],
      
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