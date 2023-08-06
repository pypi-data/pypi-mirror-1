#!/usr/bin/env python

from distutils.core import setup

setup(name='SPTE',
      version='1.1',
      description='Simple Python Template Engine',
      author='danigm',
      author_email='dani@danigm.net',
      license="gplv3",
      keyword="templating template",
      url='http://danigm.net',
      packages=['spte_examples'],
      package_data={'spte_examples': ['*.spte']},
      py_modules=['spte'],
     )

