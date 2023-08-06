#!/usr/bin/env python

from setuptools import setup
setup(name='boggleboard',
      version='1.0.0',
      description='Manipulate and analyse anagrams and variations of Boggle boards.',
      author='Sebastian Raaphorst',
      author_email='srcoding@gmail.com',
      url='http://www.site.uottawa.ca/~mraap046',
      packages=['boggleboard'],
      long_description="""
          The BoggleBoard package performs manipulations and analysis on
          Boggle-style boards (e.g. standard square boards, generic rectangular
          boards, and toroidal-style boards). Additionally, it can be used to
          search for anagrams (e.g. words in a hand of Scrabble tiles).
      """,
      classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Games/Entertainment :: Puzzle Games',
        ],
      keywords='boggle anagram anagrams board games puzzles',
      license='GPL'
      )
