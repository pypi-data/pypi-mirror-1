#!/usr/bin/env python

from distutils.core import setup

setup(name='Dejavu',
      version='1.5.0',
      description='A pure-Python Object Relational Mapper',
      author='Robert E Brewer',
      author_email='fumanchu@aminus.org',
      url='http://projects.amor.org/dejavu/',
      download_url='http://projects.amor.org/releases/dejavu/',
      packages=['dejavu', 'dejavu/storage', 'dejavu/test'],
      package_data={'dejavu': ['doc/*.html', 'doc/*.css']},
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: Public Domain',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Database :: Front-Ends',
          'Topic :: Software Development :: Libraries',
          ],
     )
