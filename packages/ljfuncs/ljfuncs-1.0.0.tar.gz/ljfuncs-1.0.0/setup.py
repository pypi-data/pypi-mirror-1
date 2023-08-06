#!/usr/bin/env python

from setuptools import setup
setup(name='ljfuncs',
      version='1.0.0',
      description='Functions for analysing friends and interests lists on Livejournal.',
      author='Sebastian Raaphorst',
      author_email='srcoding@gmail.com',
      url='http://www.site.uottawa.ca/~mraap046',
      packages=['ljfuncs'],
      long_description="""
A set of functions to query LiveJournal, primarily regarding friends, and to
make recommendations for new friends based on compatibility calculated by
interest similarities.

NOTE: This package is intended more to perform analysis on a user's friends and
on other LJ users; it is not intended for basic functionality like making posts
to LiveJournal, editing entries, etc.
      """,
      classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Communications'
        ],
      keywords='livejournal lj blogging blog',
      license='Apache 2.0'
      )
